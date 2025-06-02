from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated

from app.schemas.users import UserData, UserDataByAdmin, UserFromDB, UserUpdate, UserQueryParams
from app.services.users import User
from app.auth.dependencies import get_current_user, get_admin_user

router = APIRouter(prefix='/users')

@router.post('/register', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_201_CREATED)
async def register(user: UserData):
    return await User.create(user)


# ------ user routes
@router.get('/me', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
async def get_user_profile(current_user: Annotated[UserFromDB, Depends(get_current_user)]):
    return current_user


# ------ admin routes
@router.post('/', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
async def create_user(user: UserDataByAdmin):
    return await User.create(user)

@router.get('/', response_model=list[UserFromDB], response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_users(params: UserQueryParams = Depends()):
    return await User.get_by_params(params)

@router.get('/count', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_users_count():
    return {'users_count': await User.count()}

@router.get('/{user_id}', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def get_user_by_id(user_id: str):
    return await User.get_by_id(user_id)

@router.patch('/{user_id}', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def update_user_partial(user_id: str, user_data: UserUpdate):
    return await User.update_partial(user_id, user_data)

@router.delete('/{user_id}', status_code=status.HTTP_200_OK, dependencies=[Depends(get_admin_user)])
async def delete_user_by_id(user_id: str):
    await User.delete(user_id)
    return {'message': 'User deleted'}