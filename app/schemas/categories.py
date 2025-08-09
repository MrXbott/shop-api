from pydantic import BaseModel, ConfigDict, field_validator, Field
from pydantic.types import conlist

from typing import List, Optional

from app.schemas.common import CommonBaseModel, BaseQueryParams

class CategoryBase(BaseModel):
    name: str

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None

    model_config = ConfigDict(extra='forbid')

class CategoryFromDB(CategoryBase):
    pass

class CategoryQueryParams(BaseQueryParams):
    name: Optional[str] = Field(default=None)