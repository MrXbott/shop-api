from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List

from app.db.database import db
from app.models.users import UserCreate, UserFromDB, UserUpdate

router = APIRouter(prefix='/users')

@router.post('/', response_model=UserFromDB, response_model_by_alias=False)
async def create_user(user: UserCreate):
    result = await db.users.insert_one(user.model_dump())
    new_user = await db.users.find_one({'_id': result.inserted_id})
    if not new_user:
        raise HTTPException(500, 'Failed to fetch inserted user')
    return new_user

@router.get('/', response_model=List[UserFromDB], response_model_by_alias=False)
async def get_all_users():
    result = db.get_collection('users').find()
    users = []
    async for user in result:
        users.append(UserFromDB(**user))
    return users

@router.get('/{id}', response_model=UserFromDB, response_model_by_alias=False)
async def get_user_by_id(id: str):
    user = await db.users.find_one({'_id': ObjectId(id)})
    if not user:
        raise HTTPException(404, 'User not found')
    return user

@router.put('/{id}', response_model=UserFromDB, response_model_by_alias=False)
async def update_user_full(id: str, user: UserCreate):
    obj_id = ObjectId(id)
    result = await db.users.replace_one({'_id': obj_id}, user.model_dump())
    if result.matched_count == 0:
        raise HTTPException(404, detail='User not found')
    updated_user = await db.users.find_one({'_id': obj_id})
    if not updated_user:
        raise HTTPException(500, detail='Failed to fetch updated user')
    return updated_user

@router.patch('/{id}', response_model=UserFromDB, response_model_by_alias=False)
async def update_user_partial(id: str, user: UserUpdate):
    obj_id = ObjectId(id)
    update_data = {k: v for k, v in user.model_dump().items() if v not in (None, [], {})}
    result = await db.users.update_one({'_id': obj_id}, {'$set': update_data})
    if result.matched_count == 0:
        raise HTTPException(404, detail='User not found')
    updated_user = await db.users.find_one({'_id': obj_id})
    if not updated_user:
        raise HTTPException(500, detail='Failed to fetch updated user')
    return updated_user

@router.delete('/{id}')
async def delete_user_by_id(id: str):
    result = await db.users.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(404, detail='User not found')
    return {'message': 'User deleted'}