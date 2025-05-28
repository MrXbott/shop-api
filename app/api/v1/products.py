from fastapi import APIRouter, HTTPException

from app.schemas.products import ProductCreate, ProductUpdate, ProductFromDB
from app.db.crud import products as crud

router = APIRouter(prefix='/products')

@router.post('/', response_model=ProductFromDB)
async def create_product(product: ProductCreate):
    result = await crud.create_new_product(product.model_dump())
    if not result.inserted_id:
        raise HTTPException(500, 'Failed to insert new product')
    
    new_product = await crud.get_product_by_id(result.inserted_id)
    if not new_product:
        raise HTTPException(500, 'Failed to fetch inserted product')
    return ProductFromDB(**new_product)

@router.get('/', response_model=list[ProductFromDB], response_model_by_alias=False)
async def get_all_products():
    products = await crud.get_products()
    return [ProductFromDB(**product) for product in products]

@router.get('/{id}', response_model=ProductFromDB, response_model_by_alias=False)
async def get_product_by_id(id: str):
    product = await crud.get_product_by_id(id)
    if not product:
        raise HTTPException(404, 'Product not found')
    return ProductFromDB(**product)

@router.put('/{id}', response_model=ProductFromDB, response_model_by_alias=False)
async def update_product_full(id: str, product: ProductCreate):
    result = await crud.update_product_full(id, product.model_dump())
    if result.matched_count == 0:
        raise HTTPException(404, detail='Product not found')  

    updated_product = await crud.get_product_by_id(id)
    if not updated_product:
        raise HTTPException(500, detail='Failed to fetch updated product')
    return updated_product

@router.patch('/{id}', response_model=ProductFromDB, response_model_by_alias=False)
async def update_product_partial(id: str, product: ProductUpdate):
    update_data = {k: v for k, v in product.model_dump().items() if v not in (None, [], {})}
    result = await crud.update_product_partial(id, update_data)
    if result.matched_count == 0:
        raise HTTPException(404, detail='Product not found')
    
    updated_product = await crud.get_product_by_id(id)
    if not updated_product:
        raise HTTPException(500, detail='Failed to fetch updated product')
    return updated_product

@router.delete('/{id}')
async def delete_product_by_id(id: str):
    result = await crud.delete_product_by_id(id)
    if result.deleted_count == 0:
        raise HTTPException(404, detail='Product not found')
    return {'message': 'Product deleted'}