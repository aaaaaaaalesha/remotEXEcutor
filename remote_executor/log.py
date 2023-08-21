import logging
import subprocess
import sys
import time
from pathlib import Path

from remote_executor.settings import (
    APPLICATION_NAME,
    LOG_LEVEL,
    LOG_DIR,
    LOG_TO_FILES,
)

logger = logging.getLogger(APPLICATION_NAME)


def log_subprocess(completed_process: subprocess.CompletedProcess, logger_=logger) -> None:
    stdout: bytes | str | None = completed_process.stdout
    stderr: bytes | str | None = completed_process.stderr
    if completed_process.returncode == 0 and stdout:
        if isinstance(stdout, bytes):
            logger_.info(stdout.decode(encoding='utf-8', errors='ignore').strip())
        else:  # str
            logger_.info(stdout.strip())
    if completed_process.returncode != 0 and stderr:
        if isinstance(stderr, bytes):
            logger_.error(stderr.decode(encoding='utf-8', errors='ignore').strip())
        else:  # str
            logger_.error(stdout.strip())


if not logger.hasHandlers():
    logger.setLevel(LOG_LEVEL)

    # To use logger only, not print() + logger.info().
    cli_handler = logging.StreamHandler(stream=sys.stdout)
    cli_handler.setLevel(logging.INFO)
    cli_handler.setFormatter(logging.Formatter(fmt='%(message)s'))
    logger.addHandler(cli_handler)

    if LOG_TO_FILES:
        Path(LOG_DIR).mkdir(exist_ok=True)
        file_handler = logging.FileHandler(
            filename=str(LOG_DIR / f'remote_executor_{time.time_ns() // 1_000_000}.log'),
            encoding='utf-8',
        )
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] "%(message)s"',
            datefmt='%d.%m.%Y %H:%M:%S',
        ))
        logger.addHandler(file_handler)
