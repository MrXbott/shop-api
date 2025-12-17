from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator, field_validator
from typing import Optional, Literal
import re


def validate_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError('Password must be at least 8 characters')

    if not re.search(r'[A-Z]', value):
        raise ValueError('Password must contain at least one uppercase letter')

    if not re.search(r'[a-z]', value):
        raise ValueError('Password must contain at least one lowercase letter')

    if not re.search(r'\d', value):
        raise ValueError('Password must contain at least one number')

    if not re.search(r'[!@#$%^&*(),.?\':{}|<>]', value):
        raise ValueError('Password must contain at least one special character')

    return value

class UserBase(BaseModel):
    '''
    Base model for user data containing common fields.
    '''
    first_name: str
    last_name: str
    email: EmailStr

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class UserRegister(UserBase):
    '''
    Model for user registration data submitted by the user.
    '''
    password: str

    @model_validator(mode='before')
    def reject_role(cls, values):
        if 'role' in values:
            raise ValueError('You can\'t set role manually')
        return values
    
    @field_validator('password', mode='plain')
    def check_password(value: str) -> str:
        return validate_password(value)

class UserRegisterByAdmin(UserBase):
    '''
    Model for user registration data submitted by an admin.
    '''
    password: str
    role: Literal['admin', 'user'] = Field(default='user')

class UserCreate(UserBase):
    '''
    Model for storing new user data in the database.
    '''
    password_hash: str
    role: Literal['admin', 'user'] = Field(default='user')

class UserUpdate(BaseModel):
    '''
    Model for user data updates.
    '''
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    model_config = ConfigDict(extra='forbid')

class UserUpdateByAdmin(BaseModel):
    '''
    Model for user data updates.
    '''
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class UserFromDB(UserBase):
    '''
    Model representing user data retrieved from the database and visible for admins only.
    '''
    id: int
    role: Literal['admin', 'user']

class UserProfile(UserBase):
    '''
    Model representing user data retrieved from the database and visible for users.
    '''
    role: Literal['admin', 'user']

class UserQueryParams(BaseModel):
    '''
    Query parameters for filtering or paginating user-related queries.
    Inherits all fields from BaseQueryParams.
    '''
    limit: int = Field(default=100, ge=1, le=100)
    skip: int = Field(default=0, ge=0)
    role: Optional[str] = Field(default=None)


class ChangePasswordByUser(BaseModel):
    current_password: str
    new_password: str

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def check_passwords_different(cls, values: 'ChangePasswordByUser'):
        if values.current_password == values.new_password:
            raise ValueError('The new password must not match the old one')
        return values

    @field_validator('new_password', mode='plain')
    def check_password(value: str) -> str:
        return validate_password(value)
    

class ChangePasswordByAdmin(BaseModel):
    new_password: str

    model_config = ConfigDict(extra='forbid')


