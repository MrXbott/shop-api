from pydantic import BaseModel, ConfigDict, field_validator, Field
from pydantic.types import conlist

from typing import List, Optional

from app.schemas.common import CommonBaseModel, BaseQueryParams

class CategoryBase(BaseModel):
    name: str

    model_config = ConfigDict(populate_by_name=True)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None

class CategoryFromDB(CategoryBase, CommonBaseModel):
    pass

class CategoryQueryParams(BaseQueryParams):
    name: Optional[str] = Field(default=None)