from app.db.database import db
from pymongo.results import UpdateResult
from pymongo import ReturnDocument
from bson import ObjectId

from app.db.crud.base import BaseCRUD

class ProductCRUD(BaseCRUD):
    collection = db.get_collection('products')

    @classmethod
    async def decrease_quantity_in_stock(cls, product_id: str, quantity: int) -> dict|None:
        result = await cls.collection.find_one_and_update(
            {
                '_id': ObjectId(product_id),
                'stock': {'$gte': quantity}
            }, 
            {
                '$inc': { 'stock': -quantity }
            },
            return_document=ReturnDocument.AFTER,
        )
        return result
    
    @classmethod
    async def increase_quantity_in_stock(cls, product_id: str, quantity: int) -> dict:
        result = await cls.collection.find_one_and_update(
            {
                '_id': ObjectId(product_id)
            }, 
            {
                '$inc': { 'stock': quantity }
            },
            return_document=ReturnDocument.AFTER,
        )
        return result
