import os
from pathlib import Path

import dotenv

dotenv.load_dotenv('.env')

# Base parameters.
APPLICATION_NAME = 'RemotEXEcutor'
BASE_DIR = Path(__file__).resolve().parent

# Configure logo for CLI.
LOGO_PATH = Path(BASE_DIR / 'logo.txt')
APPLICATION_LOGO = LOGO_PATH.read_text('utf-8') if LOGO_PATH.exists() else APPLICATION_NAME

# Configure logging.
LOG_LEVEL = 'DEBUG'
LOG_TO_FILES = True
LOG_DIR = BASE_DIR / 'logs'

HOSTNAME = os.environ.get('HOSTNAME', default=None)
USERNAME = os.environ.get('USERNAME', default=None)
PASSWORD = os.environ.get('PASSWORD', default=None)

MAIN_CONFIG_PATH = BASE_DIR.joinpath('config.ini')
CONFIG_ENCODING = 'UTF-8'

# Configure local configs.
LOCAL_CONFIG_NAME = 'remote_exec.yaml'
PROGRAM_KEY = 'PROGRAM'
DESCRIPTION_KEY = 'DESCRIPTION'
PRE_EXEC_KEY = 'PRE_EXEC'
BODY_KEY = 'BODY'
POST_EXEC_KEY = 'POST_EXEC'

PROGRAMS_DIR = BASE_DIR.parent / 'programs'
PROGRAMS_NIX_DIR = PROGRAMS_DIR / 'nix'
PROGRAMS_WINDOWS_DIR = PROGRAMS_DIR / 'windows'

RESULTS_DIR = BASE_DIR.parent / 'results'
