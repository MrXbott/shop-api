from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional

from app.models.common import CommonBaseModel

def rating_in_range(v):
    if v is not None and not (0.0 <= v <= 5.0):
        raise ValueError('Rating must be between 0.0 and 5.0')
    return v

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    category: str
    manufacturer: str
    rating: Optional[float] = None
    stock: int
    tags: Optional[List[str]] = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator('rating')
    def validate_rating(cls, v): 
        return rating_in_range(v)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    rating: Optional[float] = None
    stock: Optional[int] = None
    tags: Optional[List[str]] = None

    @field_validator('rating')
    def validate_rating(cls, v): 
        return rating_in_range(v)

class ProductFromDB(ProductBase, CommonBaseModel):
    pass



    
    