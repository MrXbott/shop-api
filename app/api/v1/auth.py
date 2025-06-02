from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.services.users import User
from app.auth.auth import create_access_token, verify_password
from app.schemas.token import Token
from app.schemas.users import UserFromDB

router = APIRouter(prefix='/auth')

@router.post('/token')
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    email = form_data.username
    user: UserFromDB = await User.get_by_email(email)
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    token = create_access_token({'sub': user.email, 'role': user.role})
    return Token(access_token=token, token_type='bearer')