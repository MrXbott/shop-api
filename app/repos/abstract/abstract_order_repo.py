from abc import ABC, abstractmethod
from typing import Optional

from app.schemas.orders import OrderCreate, OrderUpdate, OrderStatus, OrderFromDB


class AbstractOrderRepository(ABC):

    @abstractmethod
    async def create(self, data: OrderCreate) -> OrderFromDB:
        pass

    @abstractmethod
    async def get_by_id(self, order_id: int) -> OrderFromDB: 
        pass

    @abstractmethod
    async def count(self, user_id: Optional[int] = None) -> int:
        pass

    @abstractmethod
    async def get_by_params(self, params: dict, limit: int = 100, skip: int = 0) -> list[OrderFromDB]:
        pass
    
    @abstractmethod
    async def update_status(self, order_id: int, status: OrderStatus) -> OrderFromDB:
        pass


    