import inquirer

from remote_executor.cli.validators import host_validator

ask_hostname = (
    lambda: inquirer.text(
        message='Enter IP address or hostname you need to connect',
        validate=host_validator,
    )
)

ask_transport_type = (
    lambda transport_ports: inquirer.list_input(
        message='Choose available transport from list below',
        choices=transport_ports.keys(),
    )
)

ask_username = (
    lambda: inquirer.text(
        message='Enter username for the passed hostname',
    )
)

ask_transport_port = (
    lambda ports: inquirer.list_input(
        message='Choose one the following port for this transport',
        choices=ports,
    )
)

ask_password = (
    lambda hostname, username: inquirer.password(
        message=f'Password for {username}@{hostname}'
    )
)

ask_program_commands_list = (
    lambda program_commands: inquirer.checkbox(
        'Choose the programs/commands you want to execute on remote host',
        choices=[
            (f'{program_path.stem}: {cmd}', (program_path, cmd))
            for program_path, cmd_list in program_commands.items()
            for cmd in cmd_list
        ],
    )
)
