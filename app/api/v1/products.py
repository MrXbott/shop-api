from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.products import ProductCreate, ProductUpdate, ProductFromDB
from app.db.crud.products import Product

router = APIRouter(prefix='/products')

@router.post('/', response_model=ProductFromDB)
async def create_product(product: ProductCreate):
    result = await Product.create(product.model_dump())
    if not result.inserted_id:
        raise HTTPException(500, 'Failed to insert new product')
    
    new_product = await Product.get_by_id(result.inserted_id)
    if not new_product:
        raise HTTPException(500, 'Failed to fetch inserted product')
    return ProductFromDB(**new_product)

@router.get('/', response_model=list[ProductFromDB], response_model_by_alias=False)
async def get_products(
                category: Optional[str] = Query(None),
                limit: int = Query(100, ge=1, le=100),
                skip: int = Query(0, ge=0)
                ):
    query = {}
    if category:
        query['category'] = category
    products = await Product.get(query, limit, skip)
    return [ProductFromDB(**product) for product in products]

@router.get('/count')
async def get_products_count():
    count = await Product.get_count()
    return {'products_count': count}

@router.get('/{id}', response_model=ProductFromDB, response_model_by_alias=False)
async def get_product_by_id(id: str):
    product = await Product.get_by_id(id)
    if not product:
        raise HTTPException(404, 'Product not found')
    return ProductFromDB(**product)

@router.put('/{id}', response_model=ProductFromDB, response_model_by_alias=False)
async def update_product_full(id: str, product: ProductCreate):
    result = await Product.update_full(id, product.model_dump())
    if result.matched_count == 0:
        raise HTTPException(404, detail='Product not found')  

    updated_product = await Product.get_by_id(id)
    if not updated_product:
        raise HTTPException(500, detail='Failed to fetch updated product')
    return updated_product

@router.patch('/{id}', response_model=ProductFromDB, response_model_by_alias=False)
async def update_product_partial(id: str, product: ProductUpdate):
    update_data = {k: v for k, v in product.model_dump().items() if v not in (None, [], {})}
    result = await Product.update_partial(id, update_data)
    if result.matched_count == 0:
        raise HTTPException(404, detail='Product not found')
    
    updated_product = await Product.get_by_id(id)
    if not updated_product:
        raise HTTPException(500, detail='Failed to fetch updated product')
    return updated_product

@router.delete('/{id}')
async def delete_product_by_id(id: str):
    result = await Product.delete_by_id(id)
    if result.deleted_count == 0:
        raise HTTPException(404, detail='Product not found')
    return {'message': 'Product deleted'}