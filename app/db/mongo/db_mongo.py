from pymongo import AsyncMongoClient, ASCENDING
from pymongo.collection import Collection
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB = os.getenv('MONGO_DB')

client = AsyncMongoClient(MONGO_URI)

try:
    db = client.get_database(MONGO_DB)
    users_collection = db.get_collection('users')
    categories_collection = db.get_collection('categories')
except Exception as e:
    raise Exception('Unable to get db or collection: ', e)

async def setup_indexes():
    try:
        await users_collection.create_index([('email', ASCENDING)], unique=True)
        await categories_collection.create_index([('name', ASCENDING)], unique=True)
    except Exception as e:
        raise Exception('Error creating index:', e)

def get_mongo_collection_factory(collection_name: str):
    async def _get_collection() -> Collection:
        return db[collection_name]
    return _get_collection