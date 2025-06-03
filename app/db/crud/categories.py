from app.db.database import db

from app.db.crud.base import BaseCRUD

class CategoryCRUD(BaseCRUD):
    collection = db.get_collection('categories')