import configparser
import json
import os
import shutil
import socket
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

import inquirer
from fabric import Connection
from inquirer.errors import ValidationError
from inquirer.themes import BlueComposure
from tqdm import tqdm

INQUIRER_THEME = BlueComposure()

BASE_DIR = Path(__file__).resolve().parent
MAIN_CONFIG_PATH = BASE_DIR.joinpath('config.ini')
PROGRAMS_DIR = BASE_DIR / 'programs'
PROGRAMS_NIX_DIR = PROGRAMS_DIR / 'nix'
PROGRAMS_WINDOWS_DIR = PROGRAMS_DIR / 'windows'
LOCAL_CONFIG_NAME = 'remote_exec.ini'


def execute_commands_on_remote(
        hostname,
        username,
        password,
        remote_commands_dict
):
    def copy_directory_to_remote(conn, local_dir: Path, remote_dir):
        temp_tar_file = f"{local_dir}.tar.gz"
        shutil.make_archive(local_dir, 'gztar', local_dir)
        result = conn.put(temp_tar_file, remote_dir)
        os.remove(temp_tar_file)
        return result.remote

    temp_dir = tempfile.mkdtemp()

    try:
        with Connection(
                host=hostname,
                user=username,
                connect_kwargs={'password': password},
        ) as conn:
            remote_temp_dir = conn.run('mktemp -d').stdout.strip()

            for local_dir, commands in remote_commands_dict.items():
                remote_archive_path = copy_directory_to_remote(conn, local_dir, remote_temp_dir)
                conn.run(f'tar -xzvf {remote_archive_path} -C {remote_temp_dir}')

            for command in commands:
                # if 'chmod' in command:
                #     conn.run(f'chmod +x {os.path.join(remote_temp_dir, command.split()[-1])}')
                conn.run(f'cd {remote_temp_dir} && {command}')

            for local_dir, _ in remote_commands_dict.items():
                result_archive_path = os.path.join(temp_dir, f'{local_dir.stem}.zip')
                conn.run(f'tar -czvf {result_archive_path} -C {remote_temp_dir} .')
                conn.get(result_archive_path, result_archive_path)
    except Exception as err:
        shutil.rmtree(temp_dir)
        raise err
    finally:
        conn.run(f'rm -rf {remote_temp_dir}')

    return result_archive_path


def input_password(hostname: str, username: str) -> str:
    for i in range(5):
        password = inquirer.password(f'Password for {username}@{hostname}')
        try:
            with Connection(
                    host=hostname,
                    user=username,
                    connect_kwargs={'password': password},
                    connect_timeout=1,
            ) as conn:
                conn.run('whoami')
                return password
        except Exception:
            print('Incorrect password')

    print('Terminate program. Password retries number exceeded')
    exit(1)


def get_remote_platform(host, user, password) -> str | None:
    try:
        # Создаем подключение к удаленному хосту
        with Connection(host=host, user=user, connect_kwargs={"password": password}) as conn:
            # Проверяем операционную систему на удаленном хосте.
            if conn.run('uname', hide=True).ok:
                return 'nix'
            elif conn.run('ver', hide=True).ok:
                return 'windows'
            else:
                return None
    except Exception as e:
        print(f"Error connecting to the remote host: {e}")
        return None


def platform_program_dir(
        hostname: str,
        username: str,
        password: str,
        nix_dir=PROGRAMS_NIX_DIR,
        windows_dir=PROGRAMS_WINDOWS_DIR,
) -> Path:
    platform = get_remote_platform(hostname, username, password)
    if platform is None:
        print('Could not get the target host platform, sorry :(')
        exit(1)

    return nix_dir if platform == 'nix' else windows_dir


def parse_config(config_path=MAIN_CONFIG_PATH) -> dict:
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    return {
        section: json.loads(config.get(section, 'ports'))
        for section in config.sections()
        if config.get(section, 'ports') is not None
    }


def validate_host(_answers: dict, host_value: str) -> bool:
    try:
        subprocess.run(
            ['ping', '-c', '1', host_value],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except subprocess.CalledProcessError:
        raise ValidationError(
            value='',
            reason=f'Remote host {host_value} is unreachable for you.'
        )

    return True


def validate_port(_answers: dict, port_value: str) -> bool:
    if not port_value:
        return True
    try:
        return 1 <= int(port_value) <= 65535
    except ValueError:
        raise ValidationError(value=port_value)


def is_available_port(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    except Exception:
        return False


def get_available_transports(
        hostname: str,
        transport_ports: dict,
) -> dict:
    available_transport_ports = {}
    for transport, ports in transport_ports.items():
        available_ports = [
            port
            for port in tqdm(
                iterable=ports,
                desc=f'Processing {transport}',
                unit='port',
                dynamic_ncols=True,
            )
            if is_available_port(hostname, port)
        ]
        if available_ports:
            available_transport_ports[transport] = available_ports

    return available_transport_ports


def collect_programs(programs: dict, file: str):
    config = configparser.ConfigParser()
    config.read(file)
    for program in config.sections():
        # Check that program exists in catalog (not in config only).
        program_dir = Path(file).parent
        program_path = program_dir.joinpath(program)
        if not program_path.exists():
            continue

        programs[program_dir] = [
            config.get(program, cmd_key)
            for cmd_key in config.options(program)
        ]


def scan_programs(programs_dir: Path) -> dict[Path, list[str]]:
    programs = {}
    for root, _, files in os.walk(programs_dir):
        if LOCAL_CONFIG_NAME in files:
            collect_programs(programs, file=os.path.join(root, LOCAL_CONFIG_NAME))

    return programs


def main():
    print("Welcome to remote_exec_tool!")
    questions = [
        inquirer.Text(
            name='hostname',
            message='Enter IP address or hostname you need to connect',
            validate=validate_host,
        ),
        inquirer.Text(
            name='username',
            message='Enter username in the passed hostname',
        ),
    ]

    answers = inquirer.prompt(
        questions=questions,
        theme=INQUIRER_THEME,
    )

    hostname = answers['hostname']
    username = answers['username']

    # hostname = 'alexandrov-al'
    # username = 'alexandrov'

    # Проверяем доступность портов для различных транспортов
    transport_ports = parse_config()

    transport_ports = get_available_transports(hostname, transport_ports)
    if not transport_ports:
        print('You have no available transport ports :(')
        exit(0)

    transport_type = inquirer.list_input(
        message='Choose available transport from list below',
        choices=transport_ports.keys(),
    )
    ports = transport_ports[transport_type]
    if len(ports) > 1:
        transport_port = inquirer.list_input(
            message='Choose one the following port for this transport',
            choices=ports,
        )
    else:
        transport_port = ports[0]

    match transport_type:
        case 'SSH':
            password = input_password(hostname, username)
            programs_dir = platform_program_dir(hostname, username, password)
            program_commands = scan_programs(programs_dir)

            chosen_program_commands_list: list[tuple[Path, str]] = inquirer.checkbox(
                'Choose the programs/commands you want to execute on remote host',
                choices=[
                    (f'{program_path.stem}: {cmd}', (program_path, cmd))
                    for program_path, cmd_list in program_commands.items()
                    for cmd in cmd_list
                ],
            )
            if not chosen_program_commands_list:
                print('You have no choices for remote execution.')
                exit(1)

            # Получили словарь [путь до проги -- команда проги]
            chosen_program_commands: dict[Path, list[str]] = defaultdict(list)
            for path, command in chosen_program_commands_list:
                chosen_program_commands[path].append(command)

            # TODO: fix bugs here
            # results_path = execute_commands_on_remote(
            #     hostname,
            #     username,
            #     password,
            #     chosen_program_commands,
            # )

            print('Results:', chosen_program_commands)

        case _:
            raise NotImplementedError


if __name__ == '__main__':
    main()
