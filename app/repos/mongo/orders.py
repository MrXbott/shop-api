from bson import ObjectId
from datetime import datetime
from pymongo.results import UpdateResult
from pymongo.collection import Collection
from typing import Optional

from app.repos.abstract.abstract_order_repo import AbstractOrderRepository
from app.schemas.orders import OrderCreate, OrderFromDB, OrderItem, OrderQueryParams, OrderStatus


class OrderRepoMongo(AbstractOrderRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    async def create(self, data: OrderCreate) -> OrderFromDB:
        pass

    async def get_by_id(self, order_id: int) -> OrderFromDB: 
        pass

    async def count(self, user_id: Optional[int] = None) -> int:
        pass

    async def get_by_params(self, params: dict, limit: int = 100, skip: int = 0) -> list[OrderFromDB]:
        pass
    
    async def update_status(self, order_id: int, status: OrderStatus) -> OrderFromDB:
        pass


    # collection = db.get_collection('orders')
    
    # @classmethod
    # async def update_status(cls, order_id: str, new_status: str) -> UpdateResult:
    #     return await cls.collection.update_one(
    #         {'_id': ObjectId(order_id)}, 
    #         {'$set': {'status': new_status, 'updated_at': datetime.now()}}
    #         )
