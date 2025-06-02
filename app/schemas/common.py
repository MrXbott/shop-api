from pydantic import BaseModel, Field, ConfigDict, field_validator
from bson import ObjectId
from typing import Optional

class CommonBaseModel(BaseModel):
    id: Optional[str] = Field(default=None, alias= '_id')

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
    )

    @field_validator('id', mode='before', check_fields=False)
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

class BaseQueryParams(BaseModel):
    limit: int = Field(default=100, ge=1, le=100)
    skip: int = Field(default=0, ge=0)