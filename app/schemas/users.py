from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from typing import List, Optional, Literal

from app.schemas.common import CommonBaseModel, BaseQueryParams

class UserBase(BaseModel):
    """
    Base model for user data containing common fields.

    Attributes:
        name (str): The name of the user.
        email (EmailStr): The email address of the user.
    """
    name: str
    email: EmailStr

    model_config = ConfigDict(populate_by_name=True)

class UserData(UserBase):
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

class UserDataByAdmin(UserBase):
    """
    Model for user registration data submitted by an admin.

    Attributes:
        password (str): The password for the new user.
        role (Literal['admin', 'user']): The role assigned by the admin. Defaults to 'user'.
    """
    password: str
    role: Literal['admin', 'user'] = Field(default='user')

class UserCreate(UserBase):
    """
    Model for storing new user data in the database.

    Attributes:
        password_hash (str): The hashed password of the user.
        role (Literal['admin', 'user']): The role of the user. Defaults to 'user'.
    """
    password_hash: str
    role: Literal['admin', 'user'] = Field(default='user')

class UserUpdate(BaseModel):
    """
    Model for user data updates.

    Attributes:
        name (Optional[str]): The new name for the user (if provided).
    """
    name: Optional[str] = None

class UserFromDB(UserBase, CommonBaseModel):
    """
    Model representing user data retrieved from the database.

    Attributes:
        password_hash (str): The hashed password of the user.
        role (Literal['admin', 'user']): The role of the user.
    """
    password_hash: str
    role: Literal['admin', 'user']

class UserQueryParams(BaseQueryParams):
    """
    Query parameters for filtering or paginating user-related queries.

    Inherits all fields from BaseQueryParams.
    """
    pass