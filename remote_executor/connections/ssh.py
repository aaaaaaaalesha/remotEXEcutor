import os
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path

from fabric import Connection

from remote_executor.cli.questions import (
    ask_password,
    ask_program_commands_list,
)
from remote_executor.logger import logger
from remote_executor.connections.utils import scan_programs
from remote_executor.settings import (
    PROGRAMS_NIX_DIR,
    PROGRAMS_WINDOWS_DIR,
    LOCAL_CONFIG_NAME,
    PROGRAMS_DIR,
)


def process_ssh(hostname, username, port=22):
    password = request_password(hostname, username)
    programs_dir = platform_program_dir(hostname, username, password)
    program_commands = scan_programs(programs_dir)

    if not program_commands:
        msg = (
            'You have no choices for remote execution. '
            f'Please, add {LOCAL_CONFIG_NAME} near executable in {PROGRAMS_DIR}.'
        )
        logger.error(msg)
        exit(1)

    chosen_program_commands_list: list[tuple[Path, str]] = ask_program_commands_list(program_commands)

    if not chosen_program_commands_list:
        logger.info('You have choose nothing. Ok, goodbye...')
        exit(0)

    # Получили словарь [путь до проги -- команда проги].
    chosen_program_commands: dict[Path, list[str]] = defaultdict(list)
    for path, command in chosen_program_commands_list:
        chosen_program_commands[path].append(command)

    # TODO: fix bugs here
    results_path = execute_commands_on_remote(
        hostname,
        username,
        password,
        chosen_program_commands,
    )

    logger.info('Results:', results_path)


def execute_commands_on_remote(
        hostname,
        username,
        password,
        remote_commands_dict
):
    """

    :param hostname:
    :param username:
    :param password:
    :param remote_commands_dict:
    :return:
    """

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


def get_remote_platform(host, user, password) -> str | None:
    """

    :param host:
    :param user:
    :param password:
    :return:
    """
    try:
        # Создаем подключение к удаленному хосту.
        with Connection(host=host, user=user, connect_kwargs={'password': password}) as conn:
            # Проверяем операционную систему на удаленном хосте.
            if conn.run('uname', hide=True).ok:
                return 'nix'
            elif conn.run('ver', hide=True).ok:
                return 'windows'
            else:
                return None
    except Exception as e:
        logger.error(f"Error connecting to the remote host: {e}")
        return None


def request_password(hostname: str, username: str, retries=5) -> str:
    for i in range(retries):
        password = ask_password(hostname, username)
        # noinspection PyBroadException
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
            logger.info('Incorrect password')

    msg = 'Terminate program. Password retries number exceeded'
    logger.error(msg)
    exit(1)


def platform_program_dir(
        hostname: str,
        username: str,
        password: str,
        nix_dir=PROGRAMS_NIX_DIR,
        windows_dir=PROGRAMS_WINDOWS_DIR,
) -> Path:
    """

    :param hostname:
    :param username:
    :param password:
    :param nix_dir:
    :param windows_dir:
    :return:
    """
    platform = get_remote_platform(hostname, username, password)
    if platform is None:
        logger.error('Could not get the target host platform, sorry :(')
        exit(1)

    return nix_dir if platform == 'nix' else windows_dir
