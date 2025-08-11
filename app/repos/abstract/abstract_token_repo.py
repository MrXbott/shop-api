from abc import ABC, abstractmethod

from app.schemas.token import AccessToken, RefreshToken, RefreshTokenFromDB
from app.models.tokens import RefreshTokenModel


class AbstractRefreshTokenRepository(ABC):
    @abstractmethod
    async def create(self, token: RefreshToken) -> RefreshTokenFromDB:
        pass

    @abstractmethod
    async def get_by_id(self, token_id: str) -> RefreshTokenFromDB|None:
        pass

    @abstractmethod
    async def mark_as_used(self, token_id: str) -> bool:
        pass

    @abstractmethod
    async def mark_all_as_used(self, user_id: int) -> bool:
        pass