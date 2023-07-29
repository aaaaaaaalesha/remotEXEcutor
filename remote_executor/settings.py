import os

from pathlib import Path

import dotenv

from inquirer.themes import BlueComposure

dotenv.load_dotenv('.env')

HOSTNAME = os.environ.get('HOSTNAME', default='hostname')
USERNAME = os.environ.get('USERNAME', default='username')
PASSWORD = os.environ.get('PASSWORD', default='password')

INQUIRER_THEME = BlueComposure()

BASE_DIR = Path(__file__).resolve().parent
MAIN_CONFIG_PATH = BASE_DIR.joinpath('config.ini')
LOCAL_CONFIG_NAME = 'remote_exec.ini'

PROGRAMS_DIR = BASE_DIR / 'programs'
PROGRAMS_NIX_DIR = PROGRAMS_DIR / 'nix'
PROGRAMS_WINDOWS_DIR = PROGRAMS_DIR / 'windows'
