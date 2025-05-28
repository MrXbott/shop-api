from app.db.database import db
from bson import ObjectId
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult

coll_name = 'products'

async def create_new_product(product_data: dict) -> InsertOneResult:
    return await db.get_collection(coll_name).insert_one(product_data)

async def get_products() -> list[dict]:
    return await db.get_collection(coll_name).find().to_list()

async def get_product_by_id(product_id: str) -> dict:
    return await db.get_collection(coll_name).find_one({'_id': ObjectId(product_id)})

async def update_product_full(product_id: str, product_data: dict) -> UpdateResult:
    return await db.get_collection(coll_name).replace_one({'_id': ObjectId(product_id)}, product_data)

async def update_product_partial(product_id: str, product_data: dict) -> UpdateResult:
    return await db.get_collection(coll_name).update_one({'_id': ObjectId(product_id)}, {'$set': product_data})

async def delete_product_by_id(product_id: str) -> DeleteResult:
    return await db.get_collection(coll_name).delete_one(({'_id': ObjectId(product_id)}))