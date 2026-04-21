from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from app.schemas.users import UserFromDB
from app.services.users import UserService
from app.services.auth import AuthService
from app.exceptions.users import UserNotFound
from app.exceptions.tokens import InvalidToken, ExpiredToken
from app.dependencies.services import get_user_service, get_auth_service
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{settings.api_prefix}/auth/login')

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], user_servise: UserService = Depends(get_user_service), auth_service: AuthService = Depends(get_auth_service)) -> UserFromDB:
    try:
        payload = auth_service.decode_token(token)
    except (InvalidToken, ExpiredToken) as e:
        raise HTTPException(e.status_code, e.message)
    
    try:
        user_id =  int(payload.sub)
        user = await user_servise.get_user_by_id(user_id, with_roles=True)
        return user
    except UserNotFound:
        raise
    except (ValueError, KeyError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Invalid or expired token')
    

# async def get_admin_user(user: UserFromDB = Depends(get_current_user)) -> UserFromDB:
#     user_roles = [role.name for role in user.roles]

#     if not 'admin' in user_roles:
#         raise HTTPException(status.HTTP_403_FORBIDDEN, 'Admin access only')
#     return user
