from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Optional

from app.schemas.common import CommonBaseModel, BaseQueryParams

class UserBase(BaseModel):
    name: str
    email: EmailStr
    interests: Optional[List[str]] = []
    contacts: Optional[dict] = {}
    skills: Optional[List[str]] = []

    model_config = ConfigDict(populate_by_name=True)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    interests: Optional[List[str]] = []
    contacts: Optional[dict] = {}
    skills: Optional[List[str]] = []

class UserFromDB(UserBase, CommonBaseModel):
    pass

class UserQueryParams(BaseQueryParams):
    pass