from app.db.database import db

from app.db.crud.base import BaseCRUD

class Product(BaseCRUD):
    collection = db.get_collection('products')