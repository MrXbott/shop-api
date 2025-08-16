from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.repos.abstract.abstract_session_repo import AbstractSessionRepository
from app.schemas.sessions import SessionFromDB
from app.models.sessions import SessionModel
from app.models.tokens import RefreshTokenModel
from app.exceptions.sessions import SessionNotFound


class SessionRepoPostgres(AbstractSessionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, user_id: int, expires_at: datetime, user_agent: str = None, ip: str = None) -> SessionFromDB:
        new_session = SessionModel(user_id=user_id, 
                                   expires_at=expires_at, 
                                   user_agent=user_agent, 
                                   ip_address=ip
                                   )
        self.session.add(new_session)
        await self.session.commit()
        await self.session.refresh(new_session)
        return SessionFromDB.model_validate(new_session)
    

    async def get_by_id(self, session_id: str) -> SessionFromDB:
        result = await self.session.execute(
            select(SessionModel)
            .where(SessionModel.id == session_id)
        )

        session = result.scalar_one_or_none()
        if not session:
            raise SessionNotFound()
        
        return SessionFromDB.model_validate(session)
    

    async def revoke_session(self, session_id: str) -> None:
        await self.session.execute(
            update(SessionModel)
            .where(SessionModel.id == session_id, SessionModel.is_active == True)
            .values(is_active=False, revoked_at=datetime.now())
        )
        # await self.session.execute(
        #     update(RefreshTokenModel)
        #     .where(RefreshTokenModel.session_id == session_id, RefreshTokenModel.is_used == False)
        #     .values(is_used=True)
        # )
        await self.session.commit()

    async def revoke_all_sessions_for_user(self, user_id: int) -> list[str]:
        current_time = datetime.now()
        result = await self.session.execute(
            update(SessionModel)
            .where(SessionModel.user_id == user_id, SessionModel.is_active == True)
            .values(is_active=False, revoked_at=current_time)
            .returning(SessionModel.id)
        )
        await self.session.commit()

        return result.scalars().all()

        # if not revoked_session_ids:
        #     return

        # await self.session.execute(
        #     update(RefreshTokenModel)
        #     .where(RefreshTokenModel.session_id.in_(revoked_session_ids), RefreshTokenModel.is_used == False)
        #     .values(is_used=True)
        # )

    async def update_last_seen(self, session_id: str) -> None:
        await self.session.execute(
            update(SessionModel)
            .where(SessionModel.id == session_id)
            .values(last_seen_at=datetime.now())
        )
        
