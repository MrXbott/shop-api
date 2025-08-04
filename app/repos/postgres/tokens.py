from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# from datetime import datetime

# from app.schemas.token import AccessToken, RefreshToken
from app.repos.abstract.abstract_token_repo import AbstractRefreshTokenRepository
from app.models.tokens import RefreshTokenModel


class RefreshTokenPostgresRepo(AbstractRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, token_id: str) -> RefreshTokenModel | None:
        result = await self.session.execute(select(RefreshTokenModel).where(RefreshTokenModel.id==token_id))
        token = result.scalar_one_or_none()
        return token

    async def mark_as_used(self, token: RefreshTokenModel) -> None:
        token.is_used = True
        await self.session.commit()
        await self.session.refresh(token)

    async def create(self, token: RefreshTokenModel) -> RefreshTokenModel:
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token
