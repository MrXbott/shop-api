from app.db.database import db
from bson import ObjectId
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult

coll_name = 'users'

async def create_new_user(user_data: dict) -> InsertOneResult:
    return await db.get_collection(coll_name).insert_one(user_data)

async def get_users() -> list[dict]:
    return await db.get_collection(coll_name).find().to_list()

async def get_user_by_id(user_id: str) -> dict:
    return await db.get_collection(coll_name).find_one({'_id': ObjectId(user_id)})

async def update_user_full(user_id: str, user_data: dict) -> UpdateResult:
    return await db.get_collection(coll_name).replace_one({'_id': ObjectId(user_id)}, user_data)

async def update_user_partial(user_id: str, user_data: dict) -> UpdateResult:
    return await db.get_collection(coll_name).update_one({'_id': ObjectId(user_id)}, {'$set': user_data})

async def delete_user_by_id(user_id: str) -> DeleteResult:
    return await db.get_collection(coll_name).delete_one(({'_id': ObjectId(user_id)}))