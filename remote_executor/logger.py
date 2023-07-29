import logging
import os
import sys
from pathlib import Path

from remote_executor.settings import (
    APPLICATION_NAME,
    LOG_LEVEL,
    LOG_DIR,
    LOG_TO_STDERR,
    LOG_TO_FILES,
)

logger = logging.getLogger(APPLICATION_NAME)

if not logger.hasHandlers():
    logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S',
    )

    if LOG_TO_STDERR:
        stderr_handler = logging.StreamHandler(stream=sys.stderr)
        stderr_handler.setFormatter(formatter)
        logger.addHandler(stderr_handler)

    if LOG_TO_FILES:
        Path(LOG_DIR).mkdir(exist_ok=True)
        file_handler = logging.FileHandler(
            filename=str(LOG_DIR / f'remote_executor_{os.getpid()}.log'),
            encoding='utf-8',
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
