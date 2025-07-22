from fastapi import HTTPException
from app.schemas.users import UserData, UserDataByAdmin, UserCreate, UserFromDB, UserUpdate, UserQueryParams
from app.db.crud.users import UserCRUD
from app.services.base import BaseService
from app.auth.auth import get_password_hash
from app.exceptions.users import UserNotFound, CreateUserException, UpdateUserException
# from app.exceptions.common import CreationError

class User(BaseService[UserData, UserFromDB, UserUpdate, UserQueryParams]):
    crud_class = UserCRUD
    return_schema_class = UserFromDB

    not_found_exception = UserNotFound
    creation_failed_exception = CreateUserException
    update_failed_exception = UpdateUserException

    @classmethod
    async def get_by_email(cls, email: str) -> UserFromDB:
        user = await UserCRUD.get_by_email(email)
        if not user:
            raise UserNotFound('User not found')
        return UserFromDB(**user)
    
    @classmethod
    async def create(cls, data: UserData|UserDataByAdmin) -> UserFromDB:
        user_data = data.model_dump()
        user_data['password_hash'] = get_password_hash(user_data['password'])
        return await super().create(UserCreate(**user_data))