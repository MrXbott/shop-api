from app.schemas.products import ProductCreate, ProductFromDB, ProductQueryParams, ProductUpdate
from app.repos.mongo.products import ProductCRUD
from app.services.base import BaseService

from app.exceptions.products import ProductNotFound, CreateProductException, UpdateProductException

class Product(BaseService[ProductCreate, ProductFromDB, ProductUpdate, ProductQueryParams]):
    crud_class = ProductCRUD
    return_schema_class = ProductFromDB

    not_found_exception = ProductNotFound
    creation_failed_exception = CreateProductException
    update_failed_exception = UpdateProductException

    @classmethod
    async def reserve(cls, product_id: str, quantity: int) -> ProductFromDB|None:
        result = await ProductCRUD.decrease_quantity_in_stock(product_id, quantity)
        return ProductFromDB(**result) if result else None
    
    @classmethod
    async def reverse_reserve(cls, product_id, quantity) -> ProductFromDB|None:
        result = await ProductCRUD.increase_quantity_in_stock(product_id, quantity)
        return ProductFromDB(**result) if result else None
