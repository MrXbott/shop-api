from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from bson import ObjectId
from typing import List, Optional

class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    interests: Optional[List[str]] = None
    contacts: Optional[dict] = None
    skills: Optional[List[str]] = None

    model_config = ConfigDict(populate_by_name=True)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    interests: Optional[List[str]] = None
    contacts: Optional[dict] = None
    skills: Optional[List[str]] = None

class UserFromDB(UserBase):
    id: str = Field(..., alias='_id')

    model_config = ConfigDict(populate_by_name=True)

    @field_validator('id', mode='before')
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v