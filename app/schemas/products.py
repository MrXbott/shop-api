from pydantic import BaseModel, ConfigDict, field_validator, Field
from pydantic.types import conlist

from typing import List, Optional

from app.schemas.common import CommonBaseModel, BaseQueryParams

class ProductBase(BaseModel):
    name: str
    description: str
    price: float = Field(..., gt=0) 
    category: str
    manufacturer: str
    rating: Optional[float] = Field(default=0.0, ge=0.0, le=5.0)   
    stock: int = Field(..., ge=0) 
    tags: Optional[List[str]] = []

    model_config = ConfigDict(populate_by_name=True)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)  
    stock: Optional[int] = Field(default=None, ge=0)
    tags: Optional[List[str]] = []
    

class ProductFromDB(ProductBase, CommonBaseModel):
    pass

class ProductQueryParams(BaseQueryParams):
    category: Optional[str] = Field(default=None)


    
    