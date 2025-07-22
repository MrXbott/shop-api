from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.products import ProductCreate, ProductUpdate, ProductFromDB, ProductQueryParams
from app.services.products import Product
from app.auth.dependencies import get_admin_user
from app.exceptions.products import ProductNotFound, CreateProductException, UpdateProductException

router = APIRouter(prefix='/products')

# ---- admin routes
@router.post('/', response_model=ProductFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def create_product(product: ProductCreate):
    try:
        return await Product.create(product)
    except CreateProductException as e:
        raise HTTPException(500, str(e))
    except ProductNotFound as e:
        raise HTTPException(404, 'Can\'t find created product')

@router.get('/count', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_products_count():
    return {'products_count': await Product.count()}

@router.put('/{product_id}', response_model=ProductFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def update_product_full(product_id: str, product_data: ProductCreate):
    try:
        return await Product.update_full(product_id, product_data)    
    except ProductNotFound as e:
        raise HTTPException(404, str(e))
    except UpdateProductException as e:
        raise HTTPException(500, str(e))

@router.patch('/{product_id}', response_model=ProductFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def update_product_partial(product_id: str, product_data: ProductUpdate):
    try:
        return await Product.update_partial(product_id, product_data)
    except ProductNotFound as e:
        raise HTTPException(404, str(e))
    except UpdateProductException as e:
        raise HTTPException(500, str(e))

@router.delete('/{product_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def delete_product_by_id(product_id: str):
    try:
        await Product.delete(product_id)
        return {'message': 'Product deleted'}
    except ProductNotFound as e:
        raise HTTPException(404, str(e))


# ---- open routes
@router.get('/', response_model=list[ProductFromDB], response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_products(params: ProductQueryParams = Depends()):
    return await Product.get_by_params(params)

@router.get('/{product_id}', response_model=ProductFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_product_by_id(product_id: str):
    try:
        return await Product.get_by_id(product_id)
    except ProductNotFound as e:
        raise HTTPException(404, str(e))


