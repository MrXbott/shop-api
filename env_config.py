import os
from dotenv import load_dotenv

load_dotenv()

PYTHONPATH = os.getenv('PYTHONPATH', '.')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))

API_PREFIX = os.getenv('API_PREFIX')


MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB = os.getenv('MONGO_DB')

POSTGRES_URL = os.getenv('POSTGRES_URL')


