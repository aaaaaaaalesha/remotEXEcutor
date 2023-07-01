import os
import dotenv

dotenv.load_dotenv('.env')

USERNAME = os.environ.get('USERNAME', default='username')
HOSTNAME = os.environ.get('HOSTNAME', default='hostname')
PASSWORD = os.environ.get('PASSWORD', default='password')
