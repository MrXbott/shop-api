from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.categories import CategoryCreate, CategoryUpdate, CategoryFromDB, CategoryQueryParams
from app.services.categories import Category
from app.auth.dependencies import get_admin_user

router = APIRouter(prefix='/categories')

# ---- admin routes
@router.post('/', response_model=CategoryFromDB, status_code=status.HTTP_201_CREATED, response_model_by_alias=False, dependencies=[Depends(get_admin_user)])
async def create_category(category: CategoryCreate):
    return await Category.create(category)

@router.get('/count', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_categories_count():
    return {'categories_count': await Category.count()}

@router.patch('/{category_id}', response_model=CategoryFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def update_category_partial(category_id: str, category_data: CategoryUpdate):
    return await Category.update_partial(category_id, category_data)

@router.delete('/{category_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def delete_category_by_id(category_id: str):
    await Category.delete(category_id)
    return {'message': 'Category deleted'}


# ---- open routes
@router.get('/', response_model=list[CategoryFromDB], response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_categories(params: CategoryQueryParams = Depends()):
    return await Category.get_by_params(params)

@router.get('/{category_id}', response_model=CategoryFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_category_by_id(category_id: str):
    return await Category.get_by_id(category_id)




