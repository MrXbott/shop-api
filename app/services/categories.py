from app.db.crud.categories import CategoryCRUD
from app.schemas.categories import CategoryCreate, CategoryFromDB, CategoryUpdate, CategoryQueryParams
from app.services.base import BaseService

class Category(BaseService[CategoryCreate, CategoryFromDB, CategoryUpdate, CategoryQueryParams]):
    crud_class = CategoryCRUD
    return_schema_class = CategoryFromDB
