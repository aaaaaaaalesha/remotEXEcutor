import configparser
import json
import os
import socket
from pathlib import Path

from tqdm import tqdm

from remote_executor.settings import (
    LOCAL_CONFIG_NAME,
    MAIN_CONFIG_PATH,
)


def is_available_port(host: str, port: int) -> bool:
    """

    :param host:
    :param port:
    :return:
    """
    # noinspection PyBroadException
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
    """

    :param hostname:
    :param transport_ports:
    :return:
    """
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


def scan_programs(programs_dir: Path) -> dict[Path, list[str]]:
    """

    :param programs_dir:
    :return:
    """
    programs = {}
    for root, _, files in os.walk(programs_dir):
        if LOCAL_CONFIG_NAME in files:
            collect_programs(programs, file=os.path.join(root, LOCAL_CONFIG_NAME))

    return programs


def collect_programs(programs: dict, file: str):
    """

    :param programs:
    :param file:
    :return:
    """
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


def parse_config(config_path=MAIN_CONFIG_PATH) -> dict:
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    return {
        section: json.loads(config.get(section, 'ports'))
        for section in config.sections()
        if config.get(section, 'ports') is not None
    }
