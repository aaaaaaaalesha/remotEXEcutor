import tempfile
from abc import abstractmethod, ABC
from pathlib import Path

from fabric import Connection


class BaseExecutor(ABC):
    def __init__(self, conn: Connection, username: str, password: str):
        self.conn = conn
        self.username = username
        self.password = password

    def _run(self, command: str, **kwargs):
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

    @abstractmethod
    def run(self):
        pass


class NixExecutor(BaseExecutor):

    def mktemp_dir(self) -> str | None:
        result = self._run('mktemp -d')
        if not result.ok:
            return None

        dir_path = result.stdout.strip()
        return dir_path

    def rm(self, path: str) -> bool:
        result = self._run(f'rm -rf {path}')
        return result.ok

    def run(self):
        pass


class WindowsExecutor(BaseExecutor):

    def mktemp_dir(self) -> Path | None:
        with tempfile.TemporaryDirectory() as tempdir:
            name = Path(tempdir).name
            result = self._run(fr'mkdir $HOME\AppData\Local\Temp\{name}')

        if not result.ok:
            return None

        return Path(fr'C:\Users\{self.username}\Local\Temp\{name}')

    def rm(self, path: str) -> bool:
        self._run(f'Remove-Item -Path "{path}" -Recurse -Force')

    def run(self):
        pass


def get_executor(platform: str, conn: Connection, username: str, password: str):
    if platform == 'nix':
        return NixExecutor(conn, username, password)
    elif platform == 'windows':
        return WindowsExecutor(conn, username, password)

    raise NotImplementedError
