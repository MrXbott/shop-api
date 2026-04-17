from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Cookie
# from fastapi.security import OAuth2PasswordRequestForm
# from typing import Annotated

from app.services.users import UserService
from app.services.auth import AuthService
from app.schemas.tokens import AccessToken, RefreshToken
from app.schemas.users import UserFromDB, UserProfile, UserRegister, UserLogin
from app.exceptions.users import UserNotFound, UserUnauthorized, CreateUserException, UserEmailAlreadyExists
from app.exceptions.tokens import TokenNotFound, InvalidToken, ExpiredToken, TokenException
from app.exceptions.sessions import SessionIdNotFound, SessionException, SessionNotFound
from app.dependencies.services import get_auth_service, get_user_service
from app.dependencies.users import get_current_user
# from app.utils.passwords import verify_password

from app.env_config import settings

router = APIRouter(prefix='/auth')


@router.post('/register', response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, service: UserService = Depends(get_user_service)):
    try:
        existing = await service.get_user_by_email(user.email)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, 'User with the email already exists')
    except UserNotFound:
        pass
    
    try:
        return await service.create_new_user(user)
    except (CreateUserException, UserEmailAlreadyExists, UserNotFound) as e:
        raise HTTPException(e.status_code, e.message)
    

@router.post('/login', response_model=dict)
async def login(request: Request, 
                response: Response, 
                login_data: UserLogin,
                auth_service: AuthService = Depends(get_auth_service)
                ) -> dict:
    try:
        user = await auth_service.authenticate_user(login_data.username, login_data.password)
    except (UserNotFound, UserUnauthorized) as e:
        raise HTTPException(e.status_code, e.message)
    
    client_host = request.client.host
    forwarded_for = request.headers.get('X-Forwarded-For')
    ip_address = forwarded_for.split(',')[0].strip() if forwarded_for else client_host
    user_agent = request.headers.get('User-Agent', 'unknown')

    access_token, refresh_token = await auth_service.login(user_id=user.id, 
                                                           user_agent=user_agent,
                                                           ip=ip_address)

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        expires=settings.refresh_token_expire_days * 24 * 60 * 60,
        samesite='lax',
        secure=False, # True for HTTPS
        path=f'{settings.api_prefix}/auth/token'  
    )

    # return AccessToken(access_token=access_token, token_type='bearer')
    return {'access_token': access_token,
            'token_type': 'bearer',
            'user': {
                'id': user.id,
                'roles': [role.name for role in user.roles],
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }


@router.post('/token', response_model=AccessToken)
async def refresh_token(request: Request, response: Response, auth_service: AuthService = Depends(get_auth_service)):
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Refresh token missing')

    try:
        new_refresh_token = await auth_service.update_refresh_token(refresh_token)
    except (InvalidToken, ExpiredToken, SessionException, SessionNotFound, TokenException) as e:
        raise HTTPException(e.status_code, e.message)

    response.set_cookie(
        key='refresh_token',
        value=new_refresh_token.refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        expires=settings.refresh_token_expire_days * 24 * 60 * 60,
        samesite='lax',
        secure=False, # True for HTTPS
        path=f'{settings.api_prefix}/auth/token'  
    )
    return AccessToken(access_token=new_refresh_token.access_token)

@router.post('/logout', dependencies=[Depends(get_current_user)])
async def logout(request: Request, response: Response, refresh_token: str = Cookie(...), auth_service: AuthService = Depends(get_auth_service)):
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    
    try:
        session_id = await auth_service.get_session_id_by_refresh_token(refresh_token)
        await auth_service.logout(session_id)
    except (InvalidToken, ExpiredToken, SessionIdNotFound) as e:
        raise HTTPException(e.status_code, e.message)

    response.delete_cookie(
        key='refresh_token',
        httponly=True,
        secure=False,
        samesite='lax', 
        path=f'{settings.api_prefix}/auth/token' 
    )

    return {'detail': 'Logged out successfully'}

