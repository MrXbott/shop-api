from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.products import ProductCreate, ProductUpdate, ProductFromDB, ProductQueryParams
from app.services.products import ProductService
from app.dependencies.users import get_admin_user
from app.exceptions.products import ProductNotFound, CreateProductException, UpdateProductException, ProductNoUpdateData
from app.dependencies.services import get_product_service

router = APIRouter(prefix='/products')

# ---- admin routes
@router.post('/', response_model=ProductFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def create_product(product_data: ProductCreate, service: ProductService = Depends(get_product_service)):
    try:
        return await service.add_new_product(product_data)
    except (ProductNotFound, CreateProductException) as e:
        raise HTTPException(e.status_code, e.message)

@router.get('/count', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_products_count(service: ProductService = Depends(get_product_service)):
    return {'products_count': await service.count_products()}

@router.patch('/{product_id}', response_model=ProductFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def update_product(product_id: str, product_data: ProductUpdate, service: ProductService = Depends(get_product_service)):
    try:
        return await service.update_product(product_id, product_data)
    except (ProductNotFound, UpdateProductException, ProductNoUpdateData) as e:
        raise HTTPException(e.status_code, e.message)

@router.delete('/{product_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def delete_product_by_id(product_id: str, service: ProductService = Depends(get_product_service)):
    try:
        await service.delete_product(product_id)
        return {'message': 'Product deleted'}
    except ProductNotFound as e:
        raise HTTPException(404, str(e))


# ---- open routes
@router.get('/', response_model=list[ProductFromDB], response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_products(params: ProductQueryParams = Depends(), service: ProductService = Depends(get_product_service)):
    return await service.get_products_by_params(params)

@router.get('/{product_id}', response_model=ProductFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_product_by_id(product_id: str, service: ProductService = Depends(get_product_service)):
    try:
        return await service.get_product_by_id(product_id)
    except ProductNotFound as e:
        raise HTTPException(404, str(e))


