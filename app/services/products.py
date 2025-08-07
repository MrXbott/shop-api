from app.schemas.products import ProductCreate, ProductFromDB, ProductQueryParams, ProductUpdate
# from app.repos.mongo.products import ProductCRUD
from app.services.base import BaseService
from app.exceptions.products import ProductNotFound, CreateProductException, UpdateProductException, ProductNoUpdateData
from app.repos.abstract.abstract_product_repo import AbstractProductRepository

class ProductService:
    def __init__(self, repo: AbstractProductRepository) -> None:
        self.repo = repo

    async def add_new_product(self, data: ProductCreate) -> ProductFromDB:
        return await self.repo.create(data)
        
    async def get_product_by_id(self, product_id: int) -> ProductFromDB:
        try:
            return await self.repo.get_by_id(product_id)
        except ProductNotFound:
            raise

    async def get_products_by_params(self, params: ProductQueryParams) -> list[ProductFromDB]:
        query = params.model_dump(exclude=['limit', 'skip'], exclude_none=True)
        return await self.repo.get_by_params(query, params.limit, params.skip)
    
    async def count_products(self) -> int:
        return await self.repo.count()
    
    async def update_product(self, product_id: int, data: ProductUpdate) -> ProductFromDB:
        try:
            return await self.repo.update_product(product_id, data)
        except (ProductNotFound, ProductNoUpdateData):
            raise

    async def delete_product(self, product_id: int) -> bool:
        try:
            return await self.repo.delete(product_id)
        except ProductNotFound:
            raise

    # crud_class = ProductCRUD
    # return_schema_class = ProductFromDB

    # not_found_exception = ProductNotFound
    # creation_failed_exception = CreateProductException
    # update_failed_exception = UpdateProductException

    # @classmethod
    # async def reserve(cls, product_id: str, quantity: int) -> ProductFromDB|None:
    #     result = await ProductCRUD.decrease_quantity_in_stock(product_id, quantity)
    #     return ProductFromDB(**result) if result else None
    
    # @classmethod
    # async def reverse_reserve(cls, product_id, quantity) -> ProductFromDB|None:
    #     result = await ProductCRUD.increase_quantity_in_stock(product_id, quantity)
    #     return ProductFromDB(**result) if result else None
