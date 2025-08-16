from abc import ABC, abstractmethod
from datetime import datetime

from app.schemas.tokens import RefreshTokenFromDB


class AbstractRefreshTokenRepository(ABC):
    @abstractmethod
    async def add_refresh_token(self, session_id: str, jti: str, expires_at: datetime) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, jti: str) -> RefreshTokenFromDB:
        pass

    @abstractmethod
    async def mark_as_used(self, session_id: str) -> None:
        pass

    @abstractmethod
    async def mark_tokens_as_used(self, session_ids: list[str]) -> None:
        pass