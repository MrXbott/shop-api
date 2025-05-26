from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List

from app.db.database import db
from app.models.products import ProductCreate, ProductUpdate, ProductFromDB

router = APIRouter(prefix='/products')

@router.post('/', response_model=ProductFromDB)
async def create_product( product: ProductCreate):
    result = await db.products.insert_one( product.model_dump())
    new_product = await db.products.find_one({'_id': result.inserted_id})
    if not new_product:
        raise HTTPException(500, 'Failed to fetch inserted product')
    return new_product

@router.get('/', response_model=List[ProductFromDB], response_model_by_alias=False)
async def get_all_products():
    result = db.get_collection('products').find()
    products = []
    async for product in result:
        products.append(ProductFromDB(**product))
    return products

@router.get('/{id}', response_model=ProductFromDB, response_model_by_alias=False)
async def get_product_by_id(id: str):
    product = await db.products.find_one({'_id': ObjectId(id)})
    if not product:
        raise HTTPException(404, 'Product not found')
    return product

@router.put('/{id}', response_model=ProductFromDB, response_model_by_alias=False)
async def update_product_full(id: str, product: ProductCreate):
    result = await db.products.replace_one({'_id': ObjectId(id)}, product.model_dump())
    if result.matched_count == 0:
        raise HTTPException(404, detail='Product not found')  
    updated_product = await db.products.find_one({'_id': ObjectId(id)})
    if not updated_product:
        raise HTTPException(500, detail='Failed to fetch updated product')
    return updated_product

@router.patch('/{id}', response_model=ProductFromDB, response_model_by_alias=False)
async def update_product_partial(id: str, product: ProductUpdate):
    obj_id = ObjectId(id)
    update_data = {k: v for k, v in product.model_dump().items() if v not in (None, [], {})}
    result = await db.products.update_one({'_id': obj_id}, {'$set': update_data})
    if result.matched_count == 0:
        raise HTTPException(404, detail='Product not found')
    updated_product = await db.products.find_one({'_id': obj_id})
    if not updated_product:
        raise HTTPException(500, detail='Failed to fetch updated product')
    return updated_product

@router.delete('/{id}')
async def delete_product_by_id(id: str):
    result = await db.products.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(404, detail='Product not found')
    return {'message': 'Product deleted'}