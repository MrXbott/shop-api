from pymongo.collection import Collection

from app.schemas.users import UserCreate, UserFromDB, UserRegister, UserRegisterByAdmin, UserUpdate
from app.repos.abstract.abstract_user_repo import AbstractUserRepository
from app.exceptions.users import UserNotFound, UserEmailAlreadyExists, UserNoUpdateData


class UserRepoMongo(AbstractUserRepository):
    def __init__(self, collection: Collection):
        self.collection = collection
    
    async def create(self, data: UserRegister|UserRegisterByAdmin) -> UserFromDB:
        pass

    
    async def get_by_id(self, user_id: int) -> UserFromDB:
        pass

    
    async def get_by_email(self, email: str) -> UserFromDB: 
        # user = await self.collection.find_one({'email': email})
        pass

    
    async def get_by_params(self, params: dict, limit: int = 100, offset: int = 0) -> list[UserFromDB]:
        pass

    async def count(self) -> int: 
        pass

    async def update_user(self, user_id: int, data: UserUpdate) -> UserFromDB:
        pass

    async def delete(self, identifier: int|str) -> bool:
        pass