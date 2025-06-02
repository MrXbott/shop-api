from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import os

from app.auth.auth import decode_access_token
from app.schemas.users import UserFromDB
from app.services.users import User

API_PREFIX = os.getenv('API_PREFIX')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{API_PREFIX}/auth/token')

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserFromDB:
    payload = decode_access_token(token)
    
    try:
        email =  payload['sub']
    except:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Invalid or expired token', {'WWW-Authenticate': 'Bearer'})
    
    user = await User.get_by_email(email)
    return user

async def get_admin_user(user: UserFromDB = Depends(get_current_user)) -> UserFromDB:
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Admin access only')
    return user
