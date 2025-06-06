from pydantic import BaseModel, field_validator, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId

from app.schemas.common import CommonBaseModel, BaseQueryParams

class CaseInsensitiveEnum(str, Enum):
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value_lower = value.lower()
            for member in cls:
                if member.value == value_lower:
                    return member
        return None
    
class OrderStatus(CaseInsensitiveEnum):
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

    @field_validator('user_id', mode='before', check_fields=False)
    def check_user_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        try:
            ObjectId(v)
        except:
            raise ValueError('Invalid user_id format')
        return v

class OrderCreate(OrderBase):
    status: OrderStatus
    created_at: datetime
    total_price: float
    updated_at: Optional[datetime] = None
    
    @field_validator('items')
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Order must contain at least one item')
        return v

class OrderUpdate(BaseModel):
    pass

class OrderFromDB(OrderBase, CommonBaseModel):
    status: OrderStatus
    created_at: datetime
    total_price: float
    updated_at: Optional[datetime] = None

class OrderQueryParams(BaseQueryParams):
    user_id: Optional[str] = Field(default=None)
    status: Optional[OrderStatus] = Field(default=None)


    
    