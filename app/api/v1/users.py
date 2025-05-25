from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List

from app.db.database import db
from app.models.users import UserCreate, UserFromDB, UserUpdate

router = APIRouter(prefix='/user')

@router.post('/', response_model=UserFromDB)
async def create_user(user: UserCreate):
    result = await db.users.insert_one(user.model_dump())
    return {**user.model_dump(), '_id': str(result.inserted_id)}

@router.get('/', response_model=List[UserFromDB], response_model_exclude_none=True)
async def get_all_users():
    result = db.get_collection('users').find()
    users = []
    async for user in result:
        users.append(UserFromDB(**user))
    return users

@router.get('/{id}', response_model=UserFromDB, response_model_exclude_none=True)
async def get_user_by_id(id: str):
    user = await db.users.find_one({'_id': ObjectId(id)})
    if not user:
        raise HTTPException(404, 'User not found')
    return user

@router.put('/{id}', response_model=UserFromDB)
async def replace_user_full(id: str, user: UserCreate):
    result = await db.users.replace_one({'_id': ObjectId(id)}, user.model_dump())
    if result.matched_count == 0:
        raise HTTPException(404, detail='User not found')
    return {**user.model_dump(), '_id': id}

@router.patch('/{id}', response_model=UserFromDB, response_model_exclude_none=True)
async def update_user_partial(id: str, user: UserUpdate):
    obj_id = ObjectId(id)
    update_data = {k: v for k, v in user.model_dump().items() if v is not None}
    result = await db.users.update_one({'_id': obj_id}, {'$set': update_data})
    if result.matched_count == 0:
        raise HTTPException(404, detail='User not found')
    updated = await db.users.find_one({'_id': obj_id})
    return updated

@router.delete('/{id}')
async def delete_user_by_id(id: str):
    result = await db.users.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(404, detail='User not found')
    return {'message': 'User deleted'}