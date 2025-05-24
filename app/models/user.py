from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    interests: Optional[List[str]] = None
    contacts: Optional[dict] = None
    skills: Optional[List[str]] = None

    class Config:
        exclude_none = True
        allow_population_by_field_name = True 

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