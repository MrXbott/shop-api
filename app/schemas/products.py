from pydantic import BaseModel, ConfigDict, field_validator, Field
from pydantic.types import conlist
from bson import ObjectId

from typing import List, Optional

from app.schemas.common import BaseQueryParams

class ProductBase(BaseModel):
    name: str
    description: str
    price: float = Field(..., gt=0) 
    category_id: Optional[int] = None
    manufacturer: str
    rating: Optional[float] = Field(default=0.0, ge=0.0, le=5.0)   
    quantity_in_stock: int = Field(..., ge=0) 
    tags: Optional[List[str]] = []

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    category_id: Optional[int] = None
    manufacturer: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)  
    quantity_in_stock: Optional[int] = Field(default=None, ge=0)
    tags: Optional[List[str]] = []

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    

class ProductFromDB(ProductBase):
    pass

class ProductQueryParams(BaseModel):
    limit: int = Field(default=100, ge=1, le=100)
    skip: int = Field(default=0, ge=0)
    category_id: Optional[int] = Field(default=None)


    
    