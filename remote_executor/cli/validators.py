import subprocess
from subprocess import CalledProcessError, TimeoutExpired

from inquirer.errors import ValidationError


def not_empty_validator(_answers: dict, value) -> bool:
    if not value:
        raise ValidationError(value='', reason='Empty input. Denied.')

    return True


def host_validator(_answers: dict, host_value: str) -> bool:
    not_empty_validator(_answers, host_value)
    try:
        subprocess.run(
            ['ping', '-n', '1', host_value],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=5,
        )
    except (CalledProcessError, TimeoutExpired):
        raise ValidationError(
            value='',
            reason=f'Remote host "{host_value}" is unreachable for you.'
        )

    return True


def port_validator(_answers: dict, port_value: str) -> bool:
    if not port_value:
        return True
    try:
        return 1 <= int(port_value) <= 65535
    except ValueError:
        raise ValidationError(value=port_value)
