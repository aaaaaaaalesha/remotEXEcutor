import inquirer
from inquirer.errors import ValidationError

from remote_executor.cli.validators import (
    not_empty_validator,
    host_validator,
)
from remote_executor.log import logger
from remote_executor.program.base import Program


def ask_hostname():
    is_valid = False
    hostname = 'localhost'
    while not is_valid:
        hostname = inquirer.text(
            message='Enter IP address or hostname you need to connect',
        )
        try:
            host_validator({}, hostname)
        except ValidationError as err:
            logger.info(err.reason)

        is_valid = ask_are_you_sure(
            f'Are you sure you want to continue with hostname "{hostname}"',
        )

    return hostname


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


def ask_are_you_sure(question: str) -> bool:
    return inquirer.confirm(
        question,
        default=True,
    )
