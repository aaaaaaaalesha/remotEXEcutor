import platform
import subprocess

from remote_executor.cli.questions import ask_password
from remote_executor.logger import logger
from remote_executor.settings import PROGRAMS_WINDOWS_DIR


def process_rdp(hostname, username, port=3389):
    system_name = platform.system()
    if system_name == 'Windows':
        windows_rdp_connect(hostname, port)
    elif system_name in ('Linux', 'Darwin'):
        nix_rdp_connect(hostname, username, port)
    else:
        logger.error(f"Unsupported operating system '{system_name}'.")
        exit(1)


def windows_rdp_connect(hostname: str, username: str, port=3389):
    try:
        subprocess.run(['cmdkey', f'/generic:{hostname}:{port}', f'/user:{username}'])
        subprocess.run(['mstsc', f'/v:{hostname}:{port}'])
    except FileNotFoundError:
        msg = '"mstsc.exe" not found. Make sure Remote Desktop Connection client is installed'
        logger.error(msg)
        alternate_mstsc = PROGRAMS_WINDOWS_DIR / 'mstsc' / 'mstsc.exe'
        if not alternate_mstsc.exists():
            logger.error(f'Alternative executable {msg} by path {alternate_mstsc}')
            exit(1)

        subprocess.run([alternate_mstsc, f'/v:{hostname}:{port}'])
    finally:
        subprocess.run(['cmdkey', f'/delete:{hostname}:{port}'])


def nix_rdp_connect(hostname: str, username: str, port=3389):
    password = request_password(hostname, username, port)
    # noinspection PyBroadException
    try:
        command = ['xfreerdp', '/cert-ignore', f'/u:{username}', f'/p:{password}', f'/v:{hostname}:{port}']
        subprocess.run(command)
    except Exception:
        logger.error(
            'No suitable remote desktop client found.\n'
            'Please install "xfreerdp" to connect to RDP on Linux/Darwin'
        )


def request_password(hostname: str, username: str, port=3389, retries=5) -> str:
    for _ in range(retries):
        # noinspection PyBroadException
        try:
            password = ask_password(hostname, username)
            subprocess.run([
                'xfreerdp',
                '/cert-ignore',
                f'/u:{username}',
                f'/p:{password}',
                f'/v:{hostname}:{port}',
            ])
            return password
        except Exception:
            logger.info('Incorrect password')
