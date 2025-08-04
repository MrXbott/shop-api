from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from typing import Optional, Literal

from app.schemas.common import BaseQueryParams

class UserBase(BaseModel):
    """
    Base model for user data containing common fields.
    """
    first_name: str
    last_name: str
    email: EmailStr

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class UserRegister(UserBase):
    """
    Model for user registration data submitted by the user.

    Attributes:
        password (str): The password provided by the user during registration.

    Validation:
        Prevents users from manually setting the role.
    """
    password: str

    @model_validator(mode='before')
    def reject_role(cls, values):
        if 'role' in values:
            raise ValueError('You can\'t set role manually')
        return values

class UserRegisterByAdmin(UserBase):
    """
    Model for user registration data submitted by an admin.
    """
    password: str
    role: Literal['admin', 'user'] = Field(default='user')

class UserCreate(UserBase):
    """
    Model for storing new user data in the database.
    """
    password_hash: str
    role: Literal['admin', 'user'] = Field(default='user')

class UserUpdate(BaseModel):
    """
    Model for user data updates.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserFromDB(UserBase):
    """
    Model representing user data retrieved from the database and visible for admins only.
    """
    password_hash: str
    id: int
    role: Literal['admin', 'user']

class UserProfile(UserBase):
    """
    Model representing user data retrieved from the database and visible for users.
    """
    role: Literal['admin', 'user']

class UserQueryParams(BaseModel):
    """
    Query parameters for filtering or paginating user-related queries.
    Inherits all fields from BaseQueryParams.
    """
    limit: int = Field(default=100, ge=1, le=100)
    skip: int = Field(default=0, ge=0)
    role: Optional[str] = Field(default=None)