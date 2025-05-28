from app.db.database import db

from app.db.crud.base import BaseCRUD

class User(BaseCRUD):
    collection = db.get_collection('users')