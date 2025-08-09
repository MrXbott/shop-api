from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime
from typing import Optional

from app.schemas.orders import OrderItem, OrderBase, OrderCreate, OrderStatus, OrderFromDB, OrderUpdate, OrderQueryParams
# from app.repos.mongo.orders import OrderRepoMongo
from app.repos.abstract.abstract_order_repo import AbstractOrderRepository
from app.services.products import ProductService
from app.services.base import BaseService
from app.exceptions.orders import OrderNotFound, InvalidStatusTransition, NotEnoughStock
from app.exceptions.users import InvalidUserIdFormat

ALLOWED_STATUS_TRANSITIONS = {
    OrderStatus.CREATED: {
        OrderStatus.WAITING_FOR_PAYMENT, 
        OrderStatus.CANCELLED
        },
    OrderStatus.WAITING_FOR_PAYMENT: {
        OrderStatus.PAID, 
        OrderStatus.CANCELLED
        },
    OrderStatus.PAID: {
        OrderStatus.SHIPPED, 
        OrderStatus.CANCELLED
        },
    OrderStatus.SHIPPED: {
        OrderStatus.COMPLETED
        },
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}

class OrderService:
    def __init__(self, repo: AbstractOrderRepository) -> None:
        self.repo = repo

    def _is_valid_status_transition(self, current_status: str, new_status: str) -> bool:
        return new_status in ALLOWED_STATUS_TRANSITIONS.get(current_status, set())

    def _calculate_total_price(self, items: list[OrderItem]) -> float:
        return sum(item.quantity * item.price_at_purchase for item in items)

    async def add_new_order(self, order: OrderBase) -> OrderFromDB:
        order_data = order.model_dump(by_alias=True, exclude_none=True)
    
        total_price = self._calculate_total_price(order.items)
        order_data.update({
            'total_price': total_price,
            'status': OrderStatus.CREATED,
            'created_at': datetime.now()
        })        
        return await self.repo.create(OrderCreate(**order_data))

    async def get_order_by_id(self, order_id: int) -> OrderFromDB:
        try:
            return await self.repo.get_by_id(order_id)
        except OrderNotFound:
            raise

    async def update_order_status(self, order_id: int, new_status: OrderStatus) -> OrderFromDB:
        try:
            order = await self.repo.get_by_id(order_id)
        except OrderNotFound:
            raise
        
        current_status = order['status']
        if not self._is_valid_status_transition(current_status, new_status):
            raise InvalidStatusTransition(current_status, new_status)
        
        try:
            return await self.repo.update_status(order_id, new_status)
        except (OrderNotFound):
            raise
    
    async def get_orders_by_params(self, params: OrderQueryParams) -> list[OrderFromDB]:
        query = params.model_dump(exclude=['limit', 'skip'], exclude_none=True)
        return await self.repo.get_by_params(query, params.limit, params.skip)

    async def count_orders(self, user_id: Optional[int] = None):
        return await self.repo.count(user_id)

