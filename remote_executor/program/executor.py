import tempfile
from abc import abstractmethod, ABC
from pathlib import Path

from fabric import Connection


class Executor(ABC):
    def __init__(self, conn: Connection, username: str, password: str):
        self.conn = conn
        self.username = username
        self.password = password

    def run(self, command: str, **kwargs):
        return self.conn.run(command, **kwargs, hide=True, warn=True)

    def put(self, filepath: Path, remote_path: str) -> str:
        result = self.conn.put(str(filepath), remote=remote_path)
        return result.remote  # возвращает путь до переданного файла

    def get(self, remote_path: str, local_path: Path):
        result = self.conn.get(remote_path, local=str(local_path))
        return result

    @abstractmethod
    def mktemp_dir(self):
        pass

    @abstractmethod
    def rm(self, path: str) -> bool:
        pass


class NixExecutor(Executor):

    def mktemp_dir(self) -> str | None:
        result = self.run('mktemp -d')
        if not result.ok:
            return None

        dir_path = result.stdout.strip()
        return dir_path

    def rm(self, path: str) -> bool:
        result = self.run(f'rm -rf {path}')
        return result.ok


class WindowsExecutor(Executor):

    def mktemp_dir(self) -> str | None:
        with tempfile.TemporaryDirectory() as tempdir:
            name = Path(tempdir).name
            result = self.run(fr'mkdir $HOME\AppData\Local\Temp\{name}')

        if not result.ok:
            return None

        result = self.run(fr'echo $HOME\AppData\Local\Temp\{name}')
        return result.stdout.strip()

    def rm(self, path: str) -> bool:
        result = self.run(f'Remove-Item -Path "{path}" -Recurse -Force')
        return result.ok


def get_executor(platform: str, conn: Connection, username: str, password: str) -> Executor:
    if platform == 'nix':
        return NixExecutor(conn, username, password)
    elif platform == 'windows':
        return WindowsExecutor(conn, username, password)

    raise NotImplementedError
