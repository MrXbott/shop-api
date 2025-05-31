from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.users import UserCreate, UserFromDB, UserUpdate, UserQueryParams
from app.services.users import User

router = APIRouter(prefix='/users')

@router.post('/', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def create_user(user: UserCreate):
    return await User.create(user)

@router.get('/', response_model=list[UserFromDB], response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_users(params: UserQueryParams = Depends()):
    return await User.get_by_params(params)

@router.get('/count', status_code=status.HTTP_200_OK)
async def get_users_count():
    return {'users_count': await User.count()}

@router.get('/{user_id}', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: str):
    return await User.get_by_id(user_id)

@router.put('/{user_id}', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def update_user_full(user_id: str, user_data: UserCreate):
    return await User.update_full(user_id, user_data)

@router.patch('/{user_id}', response_model=UserFromDB, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def update_user_partial(user_id: str, user_data: UserUpdate):
    return await User.update_partial(user_id, user_data)

@router.delete('/{user_id}', status_code=status.HTTP_200_OK)
async def delete_user_by_id(user_id: str):
    await User.delete(user_id)
    return {'message': 'User deleted'}