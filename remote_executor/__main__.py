from remote_executor.cli.options import transport_option
from remote_executor.cli.questions import (
    ask_username,
    ask_hostname,
)
from remote_executor.connections.rdp import process_rdp
from remote_executor.connections.ssh import process_ssh
from remote_executor.connections.utils import (
    get_available_transports,
    parse_config,
)
from remote_executor.log import logger
from remote_executor.settings import APPLICATION_LOGO

TRANSPORT_HANDLERS = {
    'SSH': process_ssh,
    'RDP': process_rdp,
}


def main():
    """Entrypoint. Welcome ;)"""
    logger.info(APPLICATION_LOGO)
    hostname = ask_hostname()
    # Проверяем доступность портов для различных транспортов
    transport_types: dict = get_available_transports(hostname, parse_config())
    if not transport_types:
        logger.info('You have no available transport ports :(')
        exit(0)

    username = ask_username()

    transport_type, transport_port = transport_option(transport_types)
    transport_handler = TRANSPORT_HANDLERS.get(transport_type)

    if transport_handler is None:
        logger.error(f'It seems, {transport_type} not supported yet. Wait it in the next update ;)')
        exit(1)

    transport_handler(
        hostname=hostname,
        username=username,
        port=transport_port,
    )


if __name__ == '__main__':
    main()
