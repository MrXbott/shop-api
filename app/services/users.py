from fastapi import HTTPException
from app.schemas.users import UserData, UserDataByAdmin, UserCreate, UserFromDB, UserUpdate, UserQueryParams
from app.db.crud.users import UserCRUD
from app.services.base import BaseService
from app.auth.auth import get_password_hash

class User(BaseService[UserData, UserFromDB, UserUpdate, UserQueryParams]):
    crud_class = UserCRUD
    return_schema_class = UserFromDB

    @classmethod
    async def get_by_email(cls, email: str) -> UserFromDB:
        user = await UserCRUD.get_by_email(email)
        if not user:
            raise HTTPException(404, f'{cls.__name__} not found') 
        return UserFromDB(**user)
    
    @classmethod
    async def create(cls, data: UserData|UserDataByAdmin) -> UserFromDB:
        user_data = data.model_dump()
        user_data['password_hash'] = get_password_hash(user_data['password'])
        return await super().create(UserCreate(**user_data))