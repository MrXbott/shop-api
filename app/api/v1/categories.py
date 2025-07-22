from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.categories import CategoryCreate, CategoryUpdate, CategoryFromDB, CategoryQueryParams
from app.services.categories import Category
from app.auth.dependencies import get_admin_user
from app.exceptions.categories import CategoryNotFound, CreateCategoryException, UpdateCategoryException

router = APIRouter(prefix='/categories')

# ---- admin routes
@router.post('/', response_model=CategoryFromDB, status_code=status.HTTP_201_CREATED, response_model_by_alias=False, dependencies=[Depends(get_admin_user)])
async def create_category(category: CategoryCreate):
    try:
        return await Category.create(category)
    except CreateCategoryException as e:
        raise HTTPException(500, str(e))
    except CategoryNotFound as e:
        raise HTTPException(404, 'Can\'t find created category')

@router.get('/count', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_categories_count():
    return {'categories_count': await Category.count()}

@router.patch('/{category_id}', response_model=CategoryFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def update_category_partial(category_id: str, category_data: CategoryUpdate):
    try:
        return await Category.update_partial(category_id, category_data)
    except UpdateCategoryException as e:
        raise HTTPException(500, str(e))
    except CategoryNotFound as e:
        raise HTTPException(404, str(e))

@router.delete('/{category_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def delete_category_by_id(category_id: str):
    try:
        await Category.delete(category_id)
        return {'message': 'Category deleted'}
    except CategoryNotFound as e:
        raise HTTPException(404, str(e))


# ---- open routes
@router.get('/', response_model=list[CategoryFromDB], response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_categories(params: CategoryQueryParams = Depends()):
    return await Category.get_by_params(params)

@router.get('/{category_id}', response_model=CategoryFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_category_by_id(category_id: str):
    try:
        return await Category.get_by_id(category_id)
    except CategoryNotFound as e:
        raise HTTPException(404, str(e))




