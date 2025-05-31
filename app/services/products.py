from app.schemas.products import ProductCreate, ProductFromDB, ProductQueryParams, ProductUpdate
from app.db.crud.products import ProductCRUD
from app.services.base import BaseService

class Product(BaseService[ProductCreate, ProductFromDB, ProductUpdate, ProductQueryParams]):
    crud_class = ProductCRUD
    return_schema_class = ProductFromDB
