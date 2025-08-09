from sqlalchemy import update, select, delete, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.repos.abstract.abstract_order_repo import AbstractOrderRepository
from app.models.orders import OrderModel, OrderItemModel, OrderStatus
from app.schemas.orders import OrderCreate, OrderUpdate, OrderStatus, OrderFromDB
from app.exceptions.orders import OrderNotFound


class OrderRepoPostgres(AbstractOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: OrderCreate) -> OrderFromDB:
        order_data = data.model_dump()
        items = order_data.pop('items')
        order = OrderModel(**order_data)
        self.session.add(order)
        await self.session.flush()
        
        order_items = []
        for item in items:
            new_item = OrderItemModel(**item, order_id=order.id)
            order_items.append(new_item)
        
        self.session.add_all(order_items)
        await self.session.commit()
        await self.session.refresh(order)
        
        return OrderFromDB.model_validate(order)

    async def get_by_id(self, order_id: int) -> OrderFromDB: 
        result = await self.session.execute(
            select(OrderModel)
            .options(
                selectinload(OrderModel.items)
                .selectinload(OrderItemModel.product)
                )
            .where(OrderModel.id == order_id)
            )
        order = result.scalar_one_or_none()

        if not order:
            raise OrderNotFound()
        
        return OrderFromDB.model_validate(order)

    async def count(self, user_id: Optional[int] = None) -> int:
        stmt = select(func.count(OrderModel.id))
        if user_id is not None:
            stmt = stmt.where(OrderModel.user_id == user_id)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_params(self, params: dict, limit: int = 100, skip: int = 0) -> list[OrderFromDB]:
        stmt = select(OrderModel)

        for key, value in params.items():
            if hasattr(OrderModel, key):
                stmt = stmt.where(getattr(OrderModel, key) == value)

        stmt = stmt.limit(limit).offset(skip).order_by(OrderModel.created_at)

        result = await self.session.execute(stmt)
        orders = result.scalars().all()
        return [OrderFromDB.model_validate(order) for order in orders]
    
    async def update_status(self, order_id: int, status: OrderStatus) -> OrderFromDB:
        result = await self.session.execute(
            update(OrderModel)
            .where(OrderModel.id == order_id)
            .values(status=status, updated_at=datetime.now())
            .execution_options(synchronize_session='fetch')
            .returning(OrderModel)
        )
        updated_order = result.scalar_one_or_none()
        if updated_order is None:
            raise OrderNotFound()
        
        await self.session.commit()
        return OrderFromDB.model_validate(updated_order)