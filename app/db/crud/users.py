from app.db.database import db

from app.db.crud.base import BaseCRUD

class UserCRUD(BaseCRUD):
    collection = db.get_collection('users')

    @classmethod
    async def get_by_email(cls, email: str) -> dict | None:
        return await cls.collection.find_one({'email': email})