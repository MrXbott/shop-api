from sqlalchemy import update, select, delete, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.repos.abstract.abstract_order_repo import AbstractOrderRepository
from app.models.orders import OrderModel, OrderItemModel
from app.schemas.orders import OrderCreate, OrderUpdate, OrderStatus


class OrderPostgresRepo(AbstractOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: OrderCreate) -> OrderModel:
        order_data = data.model_dump()
        order = OrderModel(**order_data)
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def get_by_id(self, order_id: int) -> OrderModel|None: 
        result = await self.session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .selectinload(OrderItemModel.product)
            .where(OrderModel.id == order_id)
            )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> list[OrderModel]: 
        result = await self.session.execute(select(OrderModel).where(OrderModel.user_id == user_id))
        return result.scalars().all()

    async def count(self, user_id: Optional[int] = None) -> int:
        stmt = select(func.count(OrderModel.id))
        if user_id is not None:
            stmt = stmt.where(OrderModel.user_id == user_id)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_params(self, params: dict, limit: int = 100, offset: int = 0) -> list[OrderModel]:
        stmt = select(OrderModel)

        for key, value in params.items():
            if hasattr(OrderModel, key):
                stmt = stmt.where(getattr(OrderModel, key) == value)

        stmt = stmt.limit(limit).offset(offset).order_by(OrderModel.created_at)

        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update_status(self, order_id: int, status: str) -> bool:
        result = await self.session.execute(
            update(OrderModel)
            .where(OrderModel.id == order_id)
            .values(status=status, updated_at=datetime.now())
            .execution_options(synchronize_session='fetch')
        )
        await self.session.commit()
        return result.rowcount > 0