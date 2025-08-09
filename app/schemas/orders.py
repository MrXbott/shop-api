from pydantic import BaseModel, field_validator, Field, ConfigDict
from typing import Optional
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
    product_id: int = Field(..., gt=0) 
    # name: str
    quantity: int = Field(..., gt=0) 
    price_at_purchase: float = Field(..., gt=0) 

class OrderBase(BaseModel):
    user_id: int
    items: list[OrderItem]

    # @field_validator('user_id', mode='before', check_fields=False)
    # def check_user_id(cls, v):
    #     if isinstance(v, ObjectId):
    #         return str(v)
    #     try:
    #         ObjectId(v)
    #     except:
    #         raise ValueError('Invalid user_id format')
    #     return v

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

class OrderFromDB(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: OrderStatus
    total_price: float
    user_id: int
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


    

class OrderQueryParams(BaseModel):
    user_id: Optional[int] = Field(default=None)
    status: Optional[OrderStatus] = Field(default=None)
    limit: int = Field(default=100, ge=1, le=100)
    skip: int = Field(default=0, ge=0)


    
    