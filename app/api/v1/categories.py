from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.categories import CategoryCreate, CategoryUpdate, CategoryFromDB, CategoryQueryParams
from app.services.categories import CategoryService
from app.dependencies.roles import RoleChecker
from app.exceptions.categories import CategoryNotFound, CreateCategoryException, UpdateCategoryException, CategoryNoUpdateData
from app.dependencies.services import get_category_service

router = APIRouter(prefix='/categories')

# ---- admin routes
@router.post('/', response_model=CategoryFromDB, status_code=status.HTTP_201_CREATED, response_model_by_alias=False, dependencies=[Depends(RoleChecker(['admin']))])
async def create_category(category_data: CategoryCreate, service: CategoryService = Depends(get_category_service)):
    try:
        return await service.add_new_category(category_data)
    except (CreateCategoryException, CategoryNotFound) as e:
        raise HTTPException(e.status_code, e.message)

@router.get('/count', status_code=status.HTTP_200_OK, dependencies=[Depends(RoleChecker(['admin']))])
async def get_categories_count(service: CategoryService = Depends(get_category_service)):
    return {'categories_count': await service.count_categories()}

@router.patch('/{category_id}', response_model=CategoryFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(RoleChecker(['admin']))])
async def update_category(category_id: int, category_data: CategoryUpdate, service: CategoryService = Depends(get_category_service)):
    try:
        return await service.update_category(category_id, category_data)
    except (CategoryNotFound, CategoryNoUpdateData, UpdateCategoryException) as e:
        raise HTTPException(e.status_code, e.message)

@router.delete('/{category_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(RoleChecker(['admin']))])
async def delete_category_by_id(category_id: int, service: CategoryService = Depends(get_category_service)):
    try:
        await service.delete_category(category_id)
        return {'message': 'Category deleted'}
    except CategoryNotFound as e:
        raise HTTPException(e.status_code, e.message)


# ---- open routes
@router.get('/', response_model=list[CategoryFromDB], response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_all_categories(service: CategoryService = Depends(get_category_service)):
    return await service.get_all_categories()

@router.get('/{category_id}', response_model=CategoryFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_category_by_id(category_id: int, service: CategoryService = Depends(get_category_service)):
    try:
        return await service.get_category_by_id(category_id)
    except CategoryNotFound as e:
        raise HTTPException(e.status_code, e.message)




