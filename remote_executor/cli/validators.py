import subprocess

from inquirer.errors import ValidationError


def host_validator(_answers: dict, host_value: str) -> bool:
    """

    :param _answers:
    :param host_value:
    :return:
    """
    try:
        subprocess.run(
            ['ping', '-n', '1', host_value],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except subprocess.CalledProcessError:
        raise ValidationError(
            value='',
            reason=f'Remote host {host_value} is unreachable for you.'
        )

    return True


def port_validator(_answers: dict, port_value: str) -> bool:
    """

    :param _answers:
    :param port_value:
    :return:
    """
    if not port_value:
        return True
    try:
        return 1 <= int(port_value) <= 65535
    except ValueError:
        raise ValidationError(value=port_value)
