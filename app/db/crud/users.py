from app.db.database import db

from app.db.crud.base import BaseCRUD

class UserCRUD(BaseCRUD):
    collection = db.get_collection('users')