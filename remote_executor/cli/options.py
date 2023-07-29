from .questions import (
    ask_transport_type,
    ask_transport_port,
)


def transport_option(transport_types: dict):
    if len(transport_types) > 1:
        transport_type = ask_transport_type(transport_types)
        ports = transport_types[transport_type]
    else:
        transport_type, ports = transport_types.popitem()

    transport_port = (
        ask_transport_port(ports)
        if len(ports) > 1 else ports[0]
    )

    return transport_type, transport_port
