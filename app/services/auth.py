
from jwt import ExpiredSignatureError, InvalidTokenError, decode, encode
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from uuid import uuid4

from app.schemas.tokens import RefreshToken
from app.schemas.users import UserFromDB
from app.models.tokens import RefreshTokenModel
from app.repos.postgres.tokens import RefreshTokenRepoPostgres
from app.repos.postgres.sessions import SessionRepoPostgres
from app.exceptions.tokens import TokenNotFound, InvalidToken, ExpiredToken, InvalidTokenPayload, TokenException
from app.exceptions.sessions import SessionIdNotFound, SessionException, SessionNotFound
from app.exceptions.users import UserNotFound, UserUnauthorized
from app.services.users import UserService
from app.utils.passwords import get_password_hash, verify_password


class AuthService:
    def __init__(self, 
                 session_repo: SessionRepoPostgres, 
                 token_repo: RefreshTokenRepoPostgres, 
                 user_service: UserService,
                 access_expire_minutes: int, 
                 refresh_expire_days: int, 
                 session_lifetime_days: int,
                 secret_key: str, 
                 algorithm: str
                 ):
        self.session_repo = session_repo
        self.token_repo = token_repo
        self.user_service = user_service
        self.refresh_expire_days = refresh_expire_days
        self.access_expire_minutes = access_expire_minutes
        self.session_lifetime_days = session_lifetime_days
        self.secret_key = secret_key
        self.algorithm = algorithm

    def _create_token(self, data: dict, expires_at: datetime, token_type: str, jti: str|None = None) -> str:
        to_encode = {
            # 'iss': ISSUER,
            # 'aud': AUDIENCE,
            # 'iat': datetime.now(),  
            'exp': int(expires_at.timestamp()), 
            'jti': jti or str(uuid4()),    
            'scope': token_type,                
            **data 
        }
        return encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        try:
            payload = decode(token, self.secret_key, algorithms=[self.algorithm])
        except ExpiredSignatureError:
            raise ExpiredToken()
        except InvalidTokenError:
            raise InvalidToken()

        if not payload:
            raise InvalidToken()
        return payload


    def create_access_token(self, user_id: int) -> str:
        return self._create_token(
            data={'sub': str(user_id)}, 
            expires_at=datetime.now() + timedelta(minutes=self.access_expire_minutes), 
            token_type='access'
            )

    def create_refresh_token(self, user_id: int, session_id: str, expires_at: datetime, jti: str|None = None) -> str:
        return self._create_token(
            data={'sub': str(user_id), 'session_id': session_id}, 
            expires_at=expires_at, 
            token_type='refresh', 
            jti=jti
            )
    

    async def add_refresh_token(self, user_id: int, session_id: str) -> str:
        jti = uuid4().hex
        expires_at = datetime.now() + timedelta(days=self.refresh_expire_days)

        new_token = RefreshTokenModel(
            id=jti,
            session_id=session_id,
            expires_at=expires_at
        )

        await self.token_repo.add_refresh_token(new_token)
        return self.create_refresh_token(user_id, session_id, expires_at, jti)


    async def update_refresh_token(self, token: RefreshToken) -> RefreshToken:
        payload = self.decode_token(token)
        
        user_id = int(payload.get('sub'))
        session_id = payload.get('session_id')
        jti = payload.get('jti')

        if not user_id or not session_id or not jti:
            raise InvalidTokenPayload()
        
        try:
            session = await self.session_repo.get_by_id(session_id)
        except SessionNotFound:
            raise
        if not session.is_active or session.expires_at < datetime.now():
            raise SessionException(message='Session expired or inactive', status_code=status.HTTP_401_UNAUTHORIZED)

        try:
            token_from_db = await self.token_repo.get_by_id(jti)
        except TokenNotFound:
            raise
        if token_from_db.is_used or token_from_db.expires_at < datetime.now():
            raise TokenException(message='Refresh token already used or expired', status_code=status.HTTP_401_UNAUTHORIZED)

        await self.token_repo.mark_as_used(token_from_db.id)

        new_jti = uuid4().hex
        expires_at = datetime.now() + timedelta(days=self.refresh_expire_days)
        new_refresh_token = self.create_refresh_token(user_id, session.id, expires_at, new_jti)
        await self.token_repo.add_refresh_token(session.id, new_jti, expires_at)

        new_access_token = self.create_access_token(user_id)

        return RefreshToken(access_token=new_access_token, refresh_token=new_refresh_token)
    
    async def get_session_id_by_refresh_token(self, refresh_token: str) -> str:
        payload = self.decode_token(refresh_token)
        session_id = payload.get('session_id')

        if not session_id:
            raise SessionIdNotFound()
        
        return session_id


    async def revoke_all_sessions_for_user(self, user_id: int) -> bool:
        # to do: make this in one transaction
        session_ids = await self.session_repo.revoke_all_sessions_for_user(user_id)
        return await self.token_repo.mark_tokens_as_used(session_ids)
    
    
    async def authenticate_user(self, email: str, password: str) -> UserFromDB:
        try:
            user = await self.user_service.get_user_by_email(email)
        except UserNotFound:
            raise

        if not verify_password(password, user.password_hash):
            raise UserUnauthorized()

        return user
    
    async def login(self, user_id: int, user_agent: str = None, ip: str = None):
        session_expires_at = datetime.now() + timedelta(days=self.session_lifetime_days)
        session = await self.session_repo.create_session(user_id, session_expires_at, user_agent, ip)

        jti = uuid4().hex
        expires_at = datetime.now() + timedelta(days=self.refresh_expire_days)

        refresh_token = self.create_refresh_token(user_id, session.id, expires_at, jti)
        await self.token_repo.add_refresh_token(session.id, jti, expires_at)

        access_token = self.create_access_token(user_id)
        return access_token, refresh_token
    
    async def logout(self, session_id: str):
        # to do: make this in one transaction 
        await self.session_repo.revoke_session(session_id)
        await self.token_repo.mark_as_used(session_id)

    async def change_password(self, user_id: int, new_password: str):
        new_password_hash = get_password_hash(new_password)
        try:
            return await self.user_service.repo.update_password(user_id, new_password_hash)
        except UserNotFound:
            raise