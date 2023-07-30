from cli.options import transport_option
from cli.questions import (
    ask_hostname,
    ask_username,
)
from remote_executor.connections.rdp import process_rdp
from remote_executor.connections.ssh import process_ssh
from remote_executor.connections.utils import (
    get_available_transports,
    parse_config,
)
from remote_executor.settings import APPLICATION_LOGO

TRANSPORT_HANDLERS = {
    'SSH': process_ssh,
    'RDP': process_rdp,
}


def main():
    """Entrypoint. Welcome ;)"""
    print(APPLICATION_LOGO)
    # hostname = 'alexandrov-al'
    # username = 'alexandrov'
    hostname = ask_hostname()
    # Проверяем доступность портов для различных транспортов
    transport_types: dict = get_available_transports(hostname, parse_config())
    if not transport_types:
        print('You have no available transport ports :(')
        exit(0)

    username = ask_username()

    transport_type, transport_port = transport_option(transport_types)
    transport_handler = TRANSPORT_HANDLERS.get(transport_type)

    if transport_handler is None:
        raise NotImplementedError

    transport_handler(
        hostname=hostname,
        username=username,
        port=transport_port,
    )


if __name__ == '__main__':
    main()
