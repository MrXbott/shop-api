from abc import ABC, abstractmethod
from typing import Optional

from app.models.orders import OrderModel
from app.schemas.orders import OrderCreate, OrderUpdate, OrderStatus


class AbstractOrderRepository(ABC):

    @abstractmethod
    async def create(self, data: OrderCreate) -> OrderModel:
        pass

    @abstractmethod
    async def get_by_id(self, order_id: int) -> OrderModel: 
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> list[OrderModel]: 
        pass

    @abstractmethod
    async def count(self, user_id: Optional[int] = None) -> int:
        pass

    @abstractmethod
    async def get_by_params(cls, params: dict, limit: int = 100, offset: int = 0) -> list[OrderModel]:
        pass
    
    @abstractmethod
    async def update_status(self, order_id: int, status: str) -> bool:
        pass

    # @abstractmethod
    # async def delete(self, order_id: int) -> bool:
    #     pass

    