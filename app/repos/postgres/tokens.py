from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
# from datetime import datetime

from app.schemas.token import AccessToken, RefreshToken, RefreshTokenFromDB
from app.repos.abstract.abstract_token_repo import AbstractRefreshTokenRepository
from app.models.tokens import RefreshTokenModel
from app.exceptions.tokens import TokenNotFound


class RefreshTokenRepoPostgres(AbstractRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token: RefreshToken) -> RefreshTokenFromDB:
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return RefreshTokenFromDB.model_validate(token)

    async def get_by_id(self, token_id: str) -> RefreshTokenFromDB | None:
        result = await self.session.execute(select(RefreshTokenModel).where(RefreshTokenModel.id==token_id))
        token = result.scalar_one_or_none()
        if token is None:
            raise TokenNotFound()
        return RefreshTokenFromDB.model_validate(token)

    async def mark_as_used(self, token_id: str) -> bool:
        result = await self.session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == token_id)
            .values(is_used=True)
            .returning(RefreshTokenModel)
        )

        updated_token = result.scalar_one_or_none()
        if updated_token is None:
            raise TokenNotFound()
        
        await self.session.commit()
        return True
        # await self.session.refresh(token)

        # result = await self.session.execute(
        #     update(OrderModel)
        #     .where(OrderModel.id == order_id)
        #     .values(status=status, updated_at=datetime.now())
        #     .execution_options(synchronize_session='fetch')
        #     .returning(OrderModel)
        # )
        # updated_order = result.scalar_one_or_none()
        # if updated_order is None:
        #     raise OrderNotFound()
        
        # await self.session.commit()
        # return OrderFromDB.model_validate(updated_order)
