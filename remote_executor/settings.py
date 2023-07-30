import logging
import os

from pathlib import Path

import dotenv

dotenv.load_dotenv('.env')

# Base parameters.
APPLICATION_NAME = 'Remote Executor'
BASE_DIR = Path(__file__).resolve().parent

# Configure logo for CLI.
LOGO_PATH = Path(BASE_DIR / 'logo.txt')
APPLICATION_LOGO = LOGO_PATH.read_text('utf-8') if LOGO_PATH.exists() else APPLICATION_NAME

# Configure logging.
LOG_LEVEL = logging.DEBUG
LOG_TO_FILES = True
LOG_DIR = BASE_DIR / 'logs'

HOSTNAME = os.environ.get('HOSTNAME', default='hostname')
USERNAME = os.environ.get('USERNAME', default='username')
PASSWORD = os.environ.get('PASSWORD', default='password')

MAIN_CONFIG_PATH = BASE_DIR.joinpath('config.ini')
LOCAL_CONFIG_NAME = 'remote_exec.ini'

PROGRAMS_DIR = BASE_DIR.parent / 'programs'
PROGRAMS_NIX_DIR = PROGRAMS_DIR / 'nix'
PROGRAMS_WINDOWS_DIR = PROGRAMS_DIR / 'windows'
