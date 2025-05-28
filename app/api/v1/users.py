from fastapi import APIRouter, HTTPException

from app.schemas.users import UserCreate, UserFromDB, UserUpdate
from app.db.crud import users as crud

router = APIRouter(prefix='/users')

@router.post('/', response_model=UserFromDB, response_model_by_alias=False)
async def create_user(user: UserCreate):
    result = await crud.create_new_user(user.model_dump())
    if not result.inserted_id:
        raise HTTPException(500, 'Failed to insert new user')
    
    new_user = await crud.get_user_by_id(result.inserted_id)
    if not new_user:
        raise HTTPException(500, 'Failed to fetch inserted user')
    return UserFromDB(**new_user)

@router.get('/', response_model=list[UserFromDB], response_model_by_alias=False)
async def get_all_users():
    result = await crud.get_users()
    return [UserFromDB(**user) for user in result]

@router.get('/{id}', response_model=UserFromDB, response_model_by_alias=False)
async def get_user_by_id(id: str):
    user = await crud.get_user_by_id(id)
    if not user:
        raise HTTPException(404, 'User not found')
    return UserFromDB(**user)

@router.put('/{id}', response_model=UserFromDB, response_model_by_alias=False)
async def update_user_full(id: str, user: UserCreate):
    result = await crud.update_user_full(id, user.model_dump())
    if result.matched_count == 0:
        raise HTTPException(404, detail='User not found')
    
    updated_user = await crud.get_user_by_id(id)
    if not updated_user:
        raise HTTPException(500, detail='Failed to fetch updated user')
    return UserFromDB(**updated_user)

@router.patch('/{id}', response_model=UserFromDB, response_model_by_alias=False)
async def update_user_partial(id: str, user: UserUpdate):
    update_data = {k: v for k, v in user.model_dump().items() if v not in (None, [], {})}
    result = await crud.update_user_partial(id, update_data)
    if result.matched_count == 0:
        raise HTTPException(404, detail='User not found')
    
    updated_user = await crud.get_user_by_id(id)
    if not updated_user:
        raise HTTPException(500, detail='Failed to fetch updated user')
    return UserFromDB(**updated_user)

@router.delete('/{id}')
async def delete_user_by_id(id: str):
    result = await crud.delete_user_by_id(id)
    if result.deleted_count == 0:
        raise HTTPException(404, detail='User not found')
    return {'message': 'User deleted'}