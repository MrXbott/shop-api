from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.users import UserRegisterByAdmin, UserFromDB, UserUpdate, UserQueryParams
from app.services.users import UserService
from app.auth.dependencies import get_admin_user
from app.dependencies import get_user_service
from app.exceptions.users import UserNotFound, CreateUserException, UpdateUserException, UserEmailAlreadyExists


router = APIRouter(prefix='/users')

# ------ admin routes
@router.post('/', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
async def create_user(user: UserRegisterByAdmin, service: UserService = Depends(get_user_service)):
    try:
        return await service.create_new_user(user)
    except CreateUserException as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
    except UserEmailAlreadyExists as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except UserNotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))

@router.get('/', response_model=list[UserFromDB], response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_users(params: UserQueryParams = Depends(), service: UserService = Depends(get_user_service)):
    return await service.get_users_by_params(params)

@router.get('/count', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_users_count(service: UserService = Depends(get_user_service)):
    return {'users_count': await service.count_users()}

@router.get('/{user_id}', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_user_by_id(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        return await service.get_user_by_id(user_id)
    except UserNotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))

@router.patch('/{user_id}', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def update_user_profile(user_id: int, user_data: UserUpdate, service: UserService = Depends(get_user_service)):
    try:
        return await service.update_user(user_id, user_data)
    except UserNotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except UpdateUserException as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.delete('/{user_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def delete_user_by_id(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        result = await service.delete_user(user_id)
        return {'message': 'User deleted'}
    except UserNotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    
    