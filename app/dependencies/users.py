from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jwt import ExpiredSignatureError, InvalidTokenError

from app.schemas.users import UserFromDB
from app.services.users import UserService
from app.services.auth import AuthService
from app.exceptions.users import UserNotFound
from app.dependencies.services import get_user_service, get_auth_service
from app.env_config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{settings.api_prefix}/auth/token')

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], user_servise: UserService = Depends(get_user_service), auth_service: AuthService = Depends(get_auth_service)) -> UserFromDB:
    try:
        payload = auth_service.decode_token(token)
    except (ExpiredSignatureError, InvalidTokenError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'The token is invalid or expired')
    
    try:
        user_id =  int(payload.get('sub'))
        user = await user_servise.get_user_by_id(user_id)
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
