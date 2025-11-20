from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AccessToken(BaseModel):
    access_token: str
    token_type: str = 'bearer' # bearer for example

class RefreshToken(AccessToken):
    refresh_token: str

class RefreshTokenFromDB(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    session_id: str
    expires_at: datetime
    is_used: bool
    created_at: datetime


class TokenPayload(BaseModel):
    sub: int
    session_id: Optional[str] = None
    jti: str
    scope: str
    exp: int

    model_config = ConfigDict(extra='allow')