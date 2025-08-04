
import jwt
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from uuid import uuid4

from env_config import REFRESH_TOKEN_EXPIRE_DAYS
from app.schemas.token import AccessToken, RefreshToken
from app.models.tokens import RefreshTokenModel
from app.repos.postgres.tokens import RefreshTokenPostgresRepo
from app.auth.auth import create_access_token, create_refresh_token, decode_token
from app.exceptions.tokens import TokenNotFound


class AuthService:
    def __init__(self, token_repo: RefreshTokenPostgresRepo):
        self.token_repo = token_repo

    async def add_refresh_token(self, user_id: int) -> str:
        jti = uuid4().hex
        expires_at = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        new_token = RefreshTokenModel(
            id=jti,
            user_id=user_id,
            expires_at=datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        await self.token_repo.create(new_token)
        return create_refresh_token(user_id, expires_at, jti)


    async def update_refresh_token(self, token: RefreshToken) -> RefreshToken:
        payload = decode_token(token)
        if not payload:
            # to do: custom exception
            raise HTTPException(status_code=401, detail='Invalid token')
        
        user_id = int(payload.get('sub'))
        token_id = payload.get('jti')

        token_from_db = await self.token_repo.get_by_id(token_id)
        if not token_from_db or token_from_db.is_used or token_from_db.expires_at < datetime.now():
            # to do: custom exception
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Token revoked or does not exist')

        await self.token_repo.mark_as_used(token_from_db)

        new_jti = uuid4().hex
        expires_at = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = create_refresh_token(user_id, expires_at, new_jti)
        new_access_token = create_access_token(user_id)

        new_token_row = RefreshTokenModel(
            id=new_jti,
            user_id=user_id,
            expires_at=expires_at
        )
        await self.token_repo.create(new_token_row)

        return RefreshToken(access_token=new_access_token, refresh_token=new_refresh_token)
    

    async def mark_refresh_token_used(self, refresh_token: str):
        payload = decode_token(refresh_token)
        if not payload:
            # to do: custom exception
            raise HTTPException(status_code=401, detail='Invalid token')
        
        token_id = payload.get('jti')
        
        token = await self.token_repo.get_by_id(token_id)
        if not token:
            raise TokenNotFound
        await self.token_repo.mark_as_used(token)
