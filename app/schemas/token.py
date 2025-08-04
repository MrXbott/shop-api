from pydantic import BaseModel

class AccessToken(BaseModel):
    '''
    Response model for access token returned upon successful authentication.
    '''
    access_token: str
    token_type: str = 'bearer' # bearer for example

class RefreshToken(AccessToken):
    refresh_token: str