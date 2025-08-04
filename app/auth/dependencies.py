from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
import os
import jwt

from app.auth.auth import decode_token
from app.schemas.users import UserFromDB
from app.services.users import UserService
from app.exceptions.users import UserNotFound
from app.dependencies import get_user_service

API_PREFIX = os.getenv('API_PREFIX')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{API_PREFIX}/auth/token')

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], servise: UserService = Depends(get_user_service)) -> UserFromDB:
    try:
        payload = decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'The token is invalid or expired')
    
    try:
        # email =  payload.get('sub')
        # user = await servise.get_user_by_email(email)
        user_id =  int(payload.get('sub'))
        user = await servise.get_user_by_id(user_id)
        return user
    except UserNotFound:
        raise
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid or expired token', 
            headers={'WWW-Authenticate': 'Bearer'}
            )
    

async def get_admin_user(user: UserFromDB = Depends(get_current_user)) -> UserFromDB:
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Admin access only')
    return user
