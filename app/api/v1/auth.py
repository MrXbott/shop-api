from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from uuid import uuid4
from datetime import datetime, timedelta
import jwt

from app.services.users import UserService
from app.services.auth import AuthService
from app.auth.auth import create_access_token, verify_password, create_refresh_token, decode_token
from app.schemas.token import AccessToken, RefreshToken
from app.schemas.users import UserFromDB, UserProfile, UserRegister
from app.exceptions.users import UserNotFound, CreateUserException, UserEmailAlreadyExists
from app.exceptions.tokens import TokenNotFound
from app.dependencies import get_auth_service, get_user_service
from app.auth.dependencies import get_current_user

from env_config import REFRESH_TOKEN_EXPIRE_DAYS, API_PREFIX

router = APIRouter(prefix='/auth')


@router.post('/register', response_model=UserProfile, response_model_by_alias=False, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, service: UserService = Depends(get_user_service)):
    try:
        existing = await service.get_user_by_email(user.email)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, 'User with the email already exists')
    except UserNotFound:
        pass
    
    try:
        return await service.create_new_user(user)
    except CreateUserException as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
    except UserEmailAlreadyExists as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))
    except UserNotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))

@router.post('/login', response_model=AccessToken)
async def login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], user_service: UserService = Depends(get_user_service), auth_service: AuthService = Depends(get_auth_service)) -> AccessToken:
    email = form_data.username
    try:
        user: UserFromDB = await user_service.get_user_by_email(email)
    except UserNotFound as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    access_token = create_access_token(user.id)
    refresh_token = await auth_service.add_refresh_token(user.id)

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite='lax',
        secure=False, # True for HTTPS
        path=f'{API_PREFIX}/auth/token'  
    )

    return AccessToken(access_token=access_token, token_type='bearer')


@router.post('/token', response_model=AccessToken)
async def refresh_token(response: Response, refresh_token: str = Cookie(...), auth_service: AuthService = Depends(get_auth_service)):
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Refresh token missing')

    new_refresh_token = await auth_service.update_refresh_token(refresh_token)

    response.set_cookie(
        key='refresh_token',
        value=new_refresh_token.refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite='lax',
        secure=False, # True for HTTPS
        path=f'{API_PREFIX}/auth/token'  
    )
    return AccessToken(access_token=new_refresh_token.access_token)

@router.post('/logout', dependencies=[Depends(get_current_user)])
async def logout(response: Response, refresh_token: str = Cookie(...), auth_service: AuthService = Depends(get_auth_service)):
    try:
        await auth_service.mark_refresh_token_used(refresh_token)
    except TokenNotFound as e:
        raise HTTPException(e.status_code, e.message)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    response.delete_cookie(
        key='refresh_token',
        httponly=True,
        secure=False,
        samesite='lax', 
        path=f'{API_PREFIX}/auth/token' 
    )

    return {'detail': 'Logged out successfully'}


@router.get('/me', response_model=UserProfile, response_model_by_alias=False, status_code=status.HTTP_200_OK)
async def get_user_profile(current_user: Annotated[UserFromDB, Depends(get_current_user)]):
    return current_user


@router.post('/change_password')
async def change_password(urrent_user: Annotated[UserFromDB, Depends(get_current_user)]):
    pass