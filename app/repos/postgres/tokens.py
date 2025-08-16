from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.schemas.tokens import AccessToken, RefreshToken, RefreshTokenFromDB
from app.repos.abstract.abstract_token_repo import AbstractRefreshTokenRepository
from app.models.tokens import RefreshTokenModel
from app.exceptions.tokens import TokenNotFound
from app.exceptions.users import UserNotFound


class RefreshTokenRepoPostgres(AbstractRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_refresh_token(self, session_id: str, jti: str, expires_at: datetime) -> None:
        new_token = RefreshTokenModel(
            id=jti,
            session_id=session_id,
            expires_at=expires_at
        )
        self.session.add(new_token)
        await self.session.commit()

    async def get_by_id(self, jti: str) -> RefreshTokenFromDB:
        result = await self.session.execute(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.id==jti)
            )
        
        token = result.scalar_one_or_none()
        if token is None:
            raise TokenNotFound()
        
        return RefreshTokenFromDB.model_validate(token)

    async def mark_as_used(self, session_id: str) -> None:
        result = await self.session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.session_id == session_id, RefreshTokenModel.is_used == False)
            .values(is_used=True)
            .returning(RefreshTokenModel.id)
        )
        await self.session.commit()

        if not result:
            raise TokenNotFound()
        

    async def mark_tokens_as_used(self, session_ids: list[str]) -> None:
        result = await self.session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.session_id.in_(session_ids), RefreshTokenModel.is_used == False)
            .values(is_used=True)
        )
        await self.session.commit()
        
        # if result.rowcount == 0:
        #     raise UserNotFound()
        
        # return True
