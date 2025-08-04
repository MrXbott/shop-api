from app.db.db_mongo import db

from app.repos.mongo.base import BaseCRUD

class UserMongoRepo(BaseCRUD):
    collection = db.get_collection('users')

    @classmethod
    async def get_by_email(cls, email: str) -> dict | None:
        return await cls.collection.find_one({'email': email})