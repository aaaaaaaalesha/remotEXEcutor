import datetime
import os
import shutil
import tarfile
import tempfile
from pathlib import Path

import tqdm
from fabric import Connection

from remote_executor.cli.questions import ask_password
from remote_executor.log import logger
from remote_executor.program.base import Program
from remote_executor.program.executor import Executor, get_executor
from remote_executor.program.utils import choose_program_scenarios
from remote_executor.settings import (
    PROGRAMS_NIX_DIR,
    PROGRAMS_WINDOWS_DIR, RESULTS_DIR,
)


def process_ssh(hostname, username, port=22):
    password = request_password(hostname, username)
    platform = get_remote_platform(hostname, username, password)
    programs_dir = platform_program_dir(hostname, username, password, platform=platform)
    ready_programs: list[Program] = choose_program_scenarios(programs_dir)

    # TODO: fix bugs here
    results_path = execute_commands_on_remote(
        hostname,
        username,
        password,
        platform,
        ready_programs,
    )
    logger.info(f'You can find results in path: {results_path}')


def execute_commands_on_remote(
        hostname,
        username,
        password,
        platform,
        programs: list[Program],
        save_dir: Path = RESULTS_DIR,
) -> Path:
    sep = '\\' if platform == 'windows' else '/'
    temp_dir_path = Path(tempfile.mkdtemp())
    remote_dir_path = None
    with Connection(host=hostname, user=username, connect_kwargs={'password': password}) as conn:
        try:
            executor: Executor = get_executor(platform, conn, username=username, password=password)
            remote_dir_path = executor.mktemp_dir()
            if remote_dir_path is None:
                logger.error('Failed to create a temporary directory on the remote host')
                return

            # Создал архив с программами (каталоги сохраняют имена).
            logger.info(f'Sending archive with executables to remote...')
            temp_archive_path = archive_programs(programs, temp_dir_path)
            remote_archive_path = executor.put(temp_archive_path, remote_dir_path)
            if not remote_archive_path:
                logger.error('Failed to upload programs archive to the remote host')
                return

            logger.info(f'Extract archive with executables in remote...')
            executor.run(f'tar -xzf {remote_archive_path} -C {remote_dir_path}')
            executor.rm(remote_archive_path)

            for program in programs:
                try:
                    remote_program_dir = f'{remote_dir_path}{sep}{program.name}'
                    # PRE_EXEC commands.
                    execute_commands(
                        executor,
                        program.pre_exec_commands,
                        remote_program_dir,
                        'PRE_EXEC',
                    )

                    for scenario in program.scenarios_on_execute:
                        execute_commands(executor, scenario.commands, remote_program_dir, scenario.name)

                except Exception as err:
                    logger.exception(err)
                finally:
                    # POST_EXEC commands.
                    execute_commands(
                        executor,
                        program.post_exec_commands,
                        remote_program_dir,
                        'POST_EXEC',
                    )

            # Collect results to local host.
            logger.info('Collecting results from remote...')
            remote_hostname = executor.get_hostname()
            remote_hostname = remote_hostname if remote_hostname else hostname
            now_dt = datetime.datetime.now()
            result_archive_path = (
                f'{remote_dir_path}{sep}'
                f'{remote_hostname}-{username}-{now_dt:%d.%m.%Y_%H-%M-%S}.tar.gz'
            )
            executor.run(f'tar -cvf {result_archive_path} {remote_dir_path}')
            save_dir.mkdir(exist_ok=True)
            results_path = save_dir / os.path.basename(result_archive_path)
            executor.get(
                remote_path=result_archive_path,
                local_path=results_path,
            )
        except Exception as err:
            raise err
        finally:
            shutil.rmtree(str(temp_dir_path))
            if remote_dir_path is not None:
                executor.rm(remote_dir_path)
            if result_archive_path is not None:
                executor.rm(result_archive_path)

    return results_path


def execute_commands(
        executor: Executor,
        commands: list[str],
        remote_program_dir: str,
        scenario_name: str,
):
    for command in commands:
        logger.info(f'Executing {scenario_name}: {command}')
        result = executor.run(f'cd {remote_program_dir} && {command}')
        if not result.ok:
            logger.error(f'Failed to execute {scenario_name}: {command}')
            if result.stderr:
                logger.error(result.stderr)


def archive_programs(programs: list[Program], temp_dir_path: Path) -> Path:
    temp_archive_path = temp_dir_path / 'programs.tar.gz'
    with tarfile.open(temp_archive_path, 'w:gz') as tar:
        for program in tqdm.tqdm(programs):
            program_dir = program.program_dir
            tar.add(program_dir, arcname=program_dir.name, recursive=True)

    return temp_archive_path


def get_remote_platform(host, user, password) -> str | None:
    try:
        with Connection(host=host, user=user, connect_kwargs={'password': password}) as conn:
            nix_res = conn.run('uname', hide=True, warn=True)
            win_res = conn.run('help', hide=True, warn=True)
            if nix_res.ok:
                return 'nix'
            elif win_res.ok:
                return 'windows'
            else:
                logger.error('Could not get the target host platform, sorry :(')
                exit(1)
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
        platform=None,
        nix_dir=PROGRAMS_NIX_DIR,
        windows_dir=PROGRAMS_WINDOWS_DIR,
) -> Path:
    if platform is None:
        platform = get_remote_platform(hostname, username, password)

    return nix_dir if platform == 'nix' else windows_dir
