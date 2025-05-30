from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.users import UserCreate, UserFromDB, UserUpdate, UserQueryParams
from app.db.crud.users import UserCRUD

from app.logger_config import logger

class User:
    @staticmethod
    async def create(user: UserCreate) -> UserFromDB:
        result = await UserCRUD.create(user.model_dump())
        if not result.inserted_id:
            raise HTTPException(500, 'Failed to insert new user')
        
        new_user = await UserCRUD.get_by_id(result.inserted_id)
        if not new_user:
            raise HTTPException(500, 'Failed to fetch inserted user')
        return UserFromDB(**new_user)
    
    @staticmethod
    async def get_by_id(user_id: str) -> UserFromDB:
        user = await UserCRUD.get_by_id(user_id)
        if not user:
            raise HTTPException(404, 'User not found')
        return UserFromDB(**user)
    
    @staticmethod
    async def get_users(params: UserQueryParams) -> list[UserFromDB]:
        query = {}
        result = await UserCRUD.get(query, params.limit, params.skip)
        users = []
        for user in result:
            try:
                users.append(UserFromDB(**user))
            except ValidationError as e:
                logger.warning('Validation error. Skip the document.', exc_info=True)
                continue
        return users
    
    @staticmethod
    async def count() -> int:
        return await UserCRUD.get_count()
    
    @staticmethod
    async def update_full(user_id: str, update_data: UserCreate) -> UserFromDB:
        result = await UserCRUD.update_full(user_id, update_data.model_dump())
        if result.matched_count == 0:
            raise HTTPException(404, detail='User not found')
        
        updated_user = await UserCRUD.get_by_id(user_id)
        if not updated_user:
            raise HTTPException(500, detail='Failed to fetch updated user')
        return UserFromDB(**updated_user)
    
    @staticmethod
    async def update_partial(user_id: str, update_data: UserUpdate) -> UserFromDB:
        data = {k: v for k, v in update_data.model_dump().items() if v not in (None, [], {})}
        result = await UserCRUD.update_partial(user_id, data)
        if result.matched_count == 0:
            raise HTTPException(404, detail='User not found')
        
        updated_user = await UserCRUD.get_by_id(user_id)
        if not updated_user:
            raise HTTPException(500, detail='Failed to fetch updated user')
        return UserFromDB(**updated_user)
    
    @staticmethod
    async def delete(user_id: str) -> None:
        result = await UserCRUD.delete_by_id(user_id)
        if result.deleted_count == 0:
            raise HTTPException(404, detail='User not found')