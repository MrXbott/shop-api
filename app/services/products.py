from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.products import ProductCreate, ProductFromDB, ProductQueryParams, ProductUpdate
from app.db.crud.products import ProductCRUD

from app.logger_config import logger

class Product:
    @staticmethod
    async def create(product: ProductCreate) -> ProductFromDB:
        result = await ProductCRUD.create(product.model_dump())
        if not result.inserted_id:
            raise HTTPException(500, 'Failed to insert new product')
        
        new_product = await ProductCRUD.get_by_id(result.inserted_id)
        if not new_product:
            raise HTTPException(500, 'Failed to fetch inserted product')
        return ProductFromDB(**new_product)
    
    @staticmethod
    async def get_by_id(product_id: str) -> ProductFromDB:
        product = await ProductCRUD.get_by_id(product_id)
        if not product:
            raise HTTPException(404, 'Product not found')
        return ProductFromDB(**product)

    @staticmethod
    async def get_products(params: ProductQueryParams) -> list[ProductFromDB]:
        query = {}
        if params.category:
            query['category'] = params.category
        result = await ProductCRUD.get(query, params.limit, params.skip)
        products = []
        
        for product in result:
            try:
                products.append(ProductFromDB(**product))
            except ValidationError as e:
                logger.warning('Validation error. Skip the document.', exc_info=True)
                continue
        return products
    
    @staticmethod
    async def count() -> int:
        return await ProductCRUD.get_count()
    
    @staticmethod
    async def update_full(product_id: str, update_data: ProductCreate) -> ProductFromDB:
        result = await ProductCRUD.update_full(product_id, update_data.model_dump())
        if result.matched_count == 0:
            raise HTTPException(404, detail='Product not found')  

        updated_product = await ProductCRUD.get_by_id(product_id)
        if not updated_product:
            raise HTTPException(500, detail='Failed to fetch updated product')
        return ProductFromDB(**updated_product)
    
    @staticmethod
    async def update_partial(product_id: str, update_data: ProductUpdate) -> ProductFromDB:
        update_data = {k: v for k, v in update_data.model_dump().items() if v not in (None, [], {})}
        result = await ProductCRUD.update_partial(product_id, update_data)
        if result.matched_count == 0:
            raise HTTPException(404, detail='Product not found')
        
        updated_product = await ProductCRUD.get_by_id(product_id)
        if not updated_product:
            raise HTTPException(500, detail='Failed to fetch updated product')
        return ProductFromDB(**updated_product)

    @staticmethod
    async def delete(product_id: str) -> None:
        result = await ProductCRUD.delete_by_id(product_id)
        if result.deleted_count == 0:
            raise HTTPException(404, detail='Product not found')
        