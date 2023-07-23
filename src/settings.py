import os

import dotenv

dotenv.load_dotenv('.env')

HOSTNAME = os.environ.get('HOSTNAME', default='hostname')
USERNAME = os.environ.get('USERNAME', default='username')
PASSWORD = os.environ.get('PASSWORD', default='password')
