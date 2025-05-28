from fastapi import APIRouter, HTTPException, Query

from app.schemas.users import UserCreate, UserFromDB, UserUpdate
from app.db.crud.users import User

router = APIRouter(prefix='/users')

@router.post('/', response_model=UserFromDB, response_model_by_alias=False)
async def create_user(user: UserCreate):
    result = await User.create(user.model_dump())
    if not result.inserted_id:
        raise HTTPException(500, 'Failed to insert new user')
    
    new_user = await User.get_by_id(result.inserted_id)
    if not new_user:
        raise HTTPException(500, 'Failed to fetch inserted user')
    return UserFromDB(**new_user)

@router.get('/', response_model=list[UserFromDB], response_model_by_alias=False)
async def get_users(
                limit: int = Query(100, ge=1, le=100),
                skip: int = Query(0, ge=0)
            ):
    result = await User.get({}, limit, skip)
    return [UserFromDB(**user) for user in result]

@router.get('/count')
async def get_users_count():
    count = await User.get_count()
    return {'users_count': count}

@router.get('/{id}', response_model=UserFromDB, response_model_by_alias=False)
async def get_user_by_id(id: str):
    user = await User.get_by_id(id)
    if not user:
        raise HTTPException(404, 'User not found')
    return UserFromDB(**user)

@router.put('/{id}', response_model=UserFromDB, response_model_by_alias=False)
async def update_user_full(id: str, user: UserCreate):
    result = await User.update_full(id, user.model_dump())
    if result.matched_count == 0:
        raise HTTPException(404, detail='User not found')
    
    updated_user = await User.get_by_id(id)
    if not updated_user:
        raise HTTPException(500, detail='Failed to fetch updated user')
    return UserFromDB(**updated_user)

@router.patch('/{id}', response_model=UserFromDB, response_model_by_alias=False)
async def update_user_partial(id: str, user: UserUpdate):
    update_data = {k: v for k, v in user.model_dump().items() if v not in (None, [], {})}
    result = await User.update_partial(id, update_data)
    if result.matched_count == 0:
        raise HTTPException(404, detail='User not found')
    
    updated_user = await User.get_by_id(id)
    if not updated_user:
        raise HTTPException(500, detail='Failed to fetch updated user')
    return UserFromDB(**updated_user)

@router.delete('/{id}')
async def delete_user_by_id(id: str):
    result = await User.delete_by_id(id)
    if result.deleted_count == 0:
        raise HTTPException(404, detail='User not found')
    return {'message': 'User deleted'}