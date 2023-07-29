import logging
import os

from pathlib import Path

import dotenv

from inquirer.themes import BlueComposure

dotenv.load_dotenv('.env')

APPLICATION_NAME = 'Remote Executor'
BASE_DIR = Path(__file__).resolve().parent

LOG_LEVEL = logging.DEBUG
LOG_TO_STDERR = True
LOG_TO_FILES = True
LOG_DIR = BASE_DIR / 'log'

HOSTNAME = os.environ.get('HOSTNAME', default='hostname')
USERNAME = os.environ.get('USERNAME', default='username')
PASSWORD = os.environ.get('PASSWORD', default='password')

INQUIRER_THEME = BlueComposure()


MAIN_CONFIG_PATH = BASE_DIR.joinpath('config.ini')
LOCAL_CONFIG_NAME = 'remote_exec.ini'

PROGRAMS_DIR = BASE_DIR.parent / 'programs'
PROGRAMS_NIX_DIR = PROGRAMS_DIR / 'nix'
PROGRAMS_WINDOWS_DIR = PROGRAMS_DIR / 'windows'
