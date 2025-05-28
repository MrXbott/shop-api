from abc import ABC
from bson import ObjectId
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from pymongo.asynchronous.collection import AsyncCollection

class BaseCRUD(ABC):
    collection: AsyncCollection

    @classmethod
    async def get_by_id(cls, item_id: str) -> dict | None:
        return await cls.collection.find_one({'_id': ObjectId(item_id)})

    @classmethod
    async def get(cls, query: dict, limit: int = 10, skip: int = 0) -> list[dict]:
        return await cls.collection.find(query, collation={'locale': 'ru', 'strength': 2}).skip(skip).limit(limit).to_list(length=limit)

    @classmethod
    async def create(cls, data: dict) -> InsertOneResult:
        return await cls.collection.insert_one(data)

    @classmethod
    async def get_count(cls) -> int:
        return await cls.collection.count_documents({})
    
    @classmethod
    async def update_full(cls, item_id: str, data: dict) -> UpdateResult:
        return await cls.collection.replace_one({'_id': ObjectId(item_id)}, data)
    
    @classmethod
    async def update_partial(cls, item_id: str, data: dict) -> UpdateResult:
        return await cls.collection.update_one({'_id': ObjectId(item_id)}, {'$set': data})


    @classmethod
    async def delete_by_id(cls, item_id: str) -> DeleteResult:
        return await cls.collection.delete_one({'_id': ObjectId(item_id)})
