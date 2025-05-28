from app.db.database import db
from bson import ObjectId
from datetime import datetime
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult

collection_name = 'orders'

async def get_order_by_id(order_id: str) -> dict:
    return await db.get_collection(collection_name).find_one({'_id': ObjectId(order_id)})

async def get_orders(query: dict, limit: int, skip: int) -> list[dict]:
    return await db.get_collection(collection_name).find(query).skip(skip).limit(limit).to_list(length=limit)

async def create_new_order(order_data: dict) -> InsertOneResult:
    return await db.get_collection(collection_name).insert_one(order_data)

async def get_orders_count() -> int:
    return await db.get_collection(collection_name).count_documents({})

async def update_order_status(order_id: str, new_status: str) -> UpdateResult:
    return await db.get_collection(collection_name).update_one(
        {'_id': ObjectId(order_id)}, 
        {'$set': {'status': new_status, 'updated_at': datetime.now()}}
        )

async def delete_order_by_id(order_id: str) -> DeleteResult:
    return await db.get_collection(collection_name).delete_one(({'_id': ObjectId(order_id)}))