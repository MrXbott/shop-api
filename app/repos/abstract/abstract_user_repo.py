from abc import ABC, abstractmethod

from app.schemas.users import UserRegister, UserRegisterByAdmin, UserFromDB, UserUpdate
from app.models.users import UserModel


class AbstractUserRepository(ABC):
    @abstractmethod
    async def create(self, data: UserRegister|UserRegisterByAdmin) -> UserFromDB:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserFromDB:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserFromDB: 
        pass

    @abstractmethod
    async def get_by_params(self, params: dict, limit: int = 100, offset: int = 0) -> list[UserFromDB]:
        pass

    @abstractmethod
    async def count(self) -> int: 
        pass

    @abstractmethod
    async def update_user(self, user_id: int, data: UserUpdate) -> UserFromDB:
        pass

    @abstractmethod
    async def update_password(self, user_id: int, new_password_hash: str) -> None:
        pass

    @abstractmethod
    async def delete(self, identifier: int|str) -> bool:
        pass