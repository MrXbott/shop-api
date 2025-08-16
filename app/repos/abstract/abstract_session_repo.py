from abc import ABC, abstractmethod
from datetime import datetime

from app.schemas.sessions import SessionFromDB


class AbstractSessionRepository(ABC):
    @abstractmethod
    async def create_session(self, user_id: int, expires_at: datetime, user_agent: str = None, ip: str = None) -> SessionFromDB:
        pass

    @abstractmethod
    async def get_by_id(self, session_id: str) -> SessionFromDB:
        pass

    @abstractmethod
    async def revoke_session(self, session_id: str) -> None:
        pass

    @abstractmethod
    async def revoke_all_sessions_for_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def update_last_seen(self, session_id: str) -> None:
        pass