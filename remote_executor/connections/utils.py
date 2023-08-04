import configparser
import json
import socket
import subprocess

from tqdm import tqdm

from remote_executor.log import log_subprocess
from remote_executor.settings import (
    MAIN_CONFIG_PATH,
    CONFIG_ENCODING,
)


def is_available_port(host: str, port: int) -> bool:
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


def parse_config(config_path=MAIN_CONFIG_PATH) -> dict:
    config = configparser.ConfigParser()
    config.read(config_path, encoding=CONFIG_ENCODING)
    return {
        section: json.loads(config.get(section, 'ports'))
        for section in config.sections()
        if config.get(section, 'ports') is not None
    }


def run(*args, log_it=True, **kwargs) -> subprocess.CompletedProcess:
    completed_process = subprocess.run(
        *args,
        capture_output=True,
        encoding='utf-8',
        **kwargs,
    )
    if log_it:
        log_subprocess(completed_process)
    return completed_process
