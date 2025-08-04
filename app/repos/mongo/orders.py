from app.db.db_mongo import db
from bson import ObjectId
from datetime import datetime
from pymongo.results import UpdateResult

from app.repos.mongo.base import BaseCRUD

class OrderCRUD(BaseCRUD):
    collection = db.get_collection('orders')
    
    @classmethod
    async def update_status(cls, order_id: str, new_status: str) -> UpdateResult:
        return await cls.collection.update_one(
            {'_id': ObjectId(order_id)}, 
            {'$set': {'status': new_status, 'updated_at': datetime.now()}}
            )
