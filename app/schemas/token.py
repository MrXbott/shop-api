from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AccessToken(BaseModel):
    '''
    Response model for access token returned upon successful authentication.
    '''
    access_token: str
    token_type: str = 'bearer' # bearer for example

class RefreshToken(AccessToken):
    refresh_token: str

class RefreshTokenFromDB(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    user_id: int
    expires_at: datetime
    is_used: bool
    created_at: datetime