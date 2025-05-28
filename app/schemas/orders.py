from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

from app.schemas.common import CommonBaseModel

class OrderStatus(str, Enum):
    CREATED = 'created'
    WAITING_FOR_PAYMENT = 'waiting_for_payment'
    PAID = 'paid'
    SHIPPED = 'shipped'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class StatusUpdate(BaseModel):
    status: OrderStatus

class OrderItem(BaseModel):
    product_id: str
    name: str
    quantity: int
    price_at_purchase: float

class OrderBase(BaseModel):
    user_id: str
    items: List[OrderItem]

class OrderCreate(OrderBase):
    pass

class OrderFromDB(OrderBase, CommonBaseModel):
    status: OrderStatus
    created_at: datetime
    total_price: float
    updated_at: Optional[datetime] = None
    
    