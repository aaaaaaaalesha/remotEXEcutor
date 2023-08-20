import shutil
import tempfile
from pathlib import Path

from pypsexec.client import Client

from remote_executor.cli.questions import (
    ask_password,
    ask_programs,
    ask_scenarios,
    ask_are_you_sure,
)
from remote_executor.program.base import scan_programs, Program
from remote_executor.log import logger
from remote_executor.program.utils import choose_program_scenarios
from remote_executor.settings import (
    PROGRAMS_WINDOWS_DIR,
    LOCAL_CONFIG_NAME,
    PROGRAMS_DIR,
)


def process_psexec(hostname, username, port=445):
    password = request_password(hostname, username)
    programs_dir = PROGRAMS_WINDOWS_DIR
    ready_programs: list[Program] = choose_program_scenarios(programs_dir)
    results_path = execute_commands_on_remote(
        hostname,
        username,
        password,
        ready_programs,
    )


def execute_commands_on_remote(
        hostname,
        username,
        password,
        programs: list[Program],
):
    sep = '\\'
    temp_dir_path = Path(tempfile.mkdtemp())
    remote_dir_path = None
    client = Client(hostname, username=username, password=password)
    try:
        client.connect()
        client.run_executable('calc.exe')
    except Exception:
        pass
    finally:
        shutil.rmtree(str(temp_dir_path))
        # if remote_dir_path is not None:
        #     executor.rm(remote_dir_path)
        client.remove_service()
        client.disconnect()


def request_password(hostname: str, username: str, retries=5) -> str:
    for i in range(retries):
        password = ask_password(hostname, username)
        client = Client(hostname, username=username, password=password)
        try:
            client.connect()
        except Exception:
            logger.info('Incorrect password')
        finally:
            client.remove_service()
            client.disconnect()

    msg = 'Terminate program. Password retries number exceeded'
    logger.error(msg)
    exit(1)
