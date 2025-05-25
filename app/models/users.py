from pydantic import BaseModel, ConfigDict, EmailStr 
from typing import List, Optional

from app.models.common import CommonBaseModel

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

class UserFromDB(UserBase, CommonBaseModel):
    pass