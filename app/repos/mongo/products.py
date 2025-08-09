from app.db.mongo.db_mongo import db
from pymongo.results import UpdateResult
from pymongo.collection import Collection
from pymongo import ReturnDocument
from bson import ObjectId

from app.schemas.products import ProductCreate, ProductUpdate, ProductFromDB
from app.repos.abstract.abstract_product_repo import AbstractProductRepository


class ProductRepoMongo(AbstractProductRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    async def create(self, data: ProductCreate) -> ProductFromDB:
        pass

    async def get_by_id(self, product_id: int) -> ProductFromDB: 
        pass

    async def count(self) -> int:
        pass

    async def get_by_params(self, params: dict, limit: int = 100, offset: int = 0) -> list[ProductFromDB]:
        pass
    
    async def update_product(self, product_id: int, data: ProductUpdate) -> ProductFromDB:
        pass

    async def delete(self, product_id: int) -> bool:
        pass

    
    # collection = db.get_collection('products')

    # @classmethod
    # async def decrease_quantity_in_stock(cls, product_id: str, quantity: int) -> dict|None:
    #     result = await cls.collection.find_one_and_update(
    #         {
    #             '_id': ObjectId(product_id),
    #             'stock': {'$gte': quantity}
    #         }, 
    #         {
    #             '$inc': { 'stock': -quantity }
    #         },
    #         return_document=ReturnDocument.AFTER,
    #     )
    #     return result
    
    # @classmethod
    # async def increase_quantity_in_stock(cls, product_id: str, quantity: int) -> dict:
    #     result = await cls.collection.find_one_and_update(
    #         {
    #             '_id': ObjectId(product_id)
    #         }, 
    #         {
    #             '$inc': { 'stock': quantity }
    #         },
    #         return_document=ReturnDocument.AFTER,
    #     )
    #     return result
