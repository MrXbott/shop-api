from app.schemas.users import UserRegister, UserRegisterByAdmin, UserCreate, UserFromDB, UserUpdate, UserQueryParams
from app.exceptions.users import UserNotFound, UserEmailAlreadyExists, UserNoUpdateData
from app.repos.abstract.abstract_user_repo import AbstractUserRepository

from passlib.context import CryptContext


class UserService:
    def __init__(self, repo: AbstractUserRepository) -> None:
        self.repo = repo

    def _get_password_hash(self, password: str) -> str:
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        return pwd_context.verify(plain_password, hashed_password)

    async def create_new_user(self, data: UserRegister|UserRegisterByAdmin) -> UserFromDB:
        user_data = data.model_dump()
        user_data['password_hash'] = self._get_password_hash(user_data['password'])
        try:
            return await self.repo.create(UserCreate(**user_data))
        except UserEmailAlreadyExists:
            raise

    async def get_user_by_id(self, user_id: int) -> UserFromDB:
        try:
            user = await self.repo.get_by_id(user_id)
        except UserNotFound:
            raise
        return user
    
    async def get_user_by_email(self, email: str) -> UserFromDB:
        try:
            user = await self.repo.get_by_email(email)
        except UserNotFound:
            raise
        return user
    
    async def get_users_by_params(self, params: UserQueryParams) -> list[UserFromDB]:
        query = params.model_dump(exclude=['limit', 'skip'], exclude_none=True)
        return await self.repo.get_by_params(query, params.limit, params.skip)
    
    async def count_users(self) -> int:
        return await self.repo.count()
    
    async def update_user(self, user_id: int, data: UserUpdate):
        try:
            return await self.repo.update_user(user_id, data)
        except (UserNotFound, UserNoUpdateData):
            raise
    
    async def change_password(self, user_id: int, new_password: str):
        new_password_hash = self._get_password_hash(new_password)
        try:
            return await self.repo.update_password(user_id, new_password_hash)
        except UserNotFound:
            raise
        
    async def delete_user(self, user_id) -> bool:
        try:
            return await self.repo.delete(user_id)
        except UserNotFound:
            raise
    