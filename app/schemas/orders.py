from pydantic import BaseModel, field_validator, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

from app.schemas.common import CommonBaseModel, BaseQueryParams

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
    quantity: int = Field(..., gt=0) 
    price_at_purchase: float = Field(..., gt=0) 

class OrderBase(BaseModel):
    user_id: str
    items: List[OrderItem]

class OrderCreate(OrderBase):
    @field_validator('items')
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Order must contain at least one item')
        return v

class OrderFromDB(OrderBase, CommonBaseModel):
    status: OrderStatus
    created_at: datetime
    total_price: float
    updated_at: Optional[datetime] = None

class OrderQueryParams(BaseQueryParams):
    user_id: Optional[str] = Field(default=None)
    status: Optional[OrderStatus] = Field(default=None)

    
    