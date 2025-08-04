from app.db.db_mongo import db

from app.repos.mongo.base import BaseCRUD

class CategoryCRUD(BaseCRUD):
    collection = db.get_collection('categories')