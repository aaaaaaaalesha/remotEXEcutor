from fabric import Connection
from invoke.exceptions import Failure

from settings import (
    USERNAME,
    HOSTNAME,
    PASSWORD,
)


def main():
    # Параметры подключения
    username, hostname = USERNAME, HOSTNAME
    password = PASSWORD

    with Connection(
            host=hostname,
            user=username,
            connect_kwargs={
                'password': password,
            }
    ) as conn:
        while True:
            pwd = conn.run('pwd', hide=True).stdout.strip()
            prefix = f'{USERNAME}@{HOSTNAME}:{pwd}$ '
            command = input(prefix)
            try:
                result = conn.run(command, hide=True)
                print(result.stdout)
            except Failure as e:
                print(e.result.stderr)


if __name__ == '__main__':
    main()
