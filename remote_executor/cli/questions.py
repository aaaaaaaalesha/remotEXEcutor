import inquirer

from remote_executor.cli.validators import (
    not_empty_validator,
    host_validator,
)
from remote_executor.program.base import Program


def ask_hostname():
    return inquirer.text(
        message='Enter IP address or hostname you need to connect',
        validate=host_validator,
    )


def ask_transport_type(transport_ports):
    return inquirer.list_input(
        message='Choose available transport from list below',
        choices=transport_ports.keys(),
    )


def ask_username() -> str:
    return inquirer.text('Enter username')


def ask_transport_port(ports):
    return inquirer.list_input(
        message='Choose one the following port for this transport',
        choices=ports,
    )


def ask_password(hostname, username):
    return inquirer.password(f'Password for {username}@{hostname}')


def ask_programs(programs: list[Program]):
    return inquirer.checkbox(
        'Choose the programs you want to execute on remote host',
        choices=[
            (f'{program.name}: {program.description[:50]}...', program)
            for program in programs
        ],
        validate=not_empty_validator,
    )


def ask_scenarios(program: Program) -> list[int]:
    return inquirer.checkbox(
        f'Choose scenarios for program {program.name}',
        choices=[
            (f'{scenario.name}: {scenario.commands}', i)
            for i, scenario in enumerate(program.body_scenarios)
        ],
        validate=not_empty_validator,
    )


def ask_are_you_sure() -> bool:
    return inquirer.confirm(
        'Do you want to start with selected options?',
        default=True,
    )
