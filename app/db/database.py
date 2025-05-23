from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
client = AsyncMongoClient(MONGO_URI)

try:
    db = client.get_database('userprofiles')
except Exception as e:
    raise Exception('Unable to get db: ', e)


