from abc import ABC, abstractmethod

from app.schemas.token import AccessToken, RefreshToken
from app.models.tokens import RefreshTokenModel


class AbstractRefreshTokenRepository(ABC):
    @abstractmethod
    async def create(self, token: RefreshToken) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, token_id: str) -> RefreshToken | None:
        pass

    @abstractmethod
    async def mark_as_used(self, token: RefreshTokenModel) -> None:
        pass