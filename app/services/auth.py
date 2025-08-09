
from jwt import ExpiredSignatureError, InvalidTokenError, decode, encode
from datetime import datetime, timedelta
from uuid import uuid4
from passlib.context import CryptContext

from app.schemas.token import RefreshToken
from app.models.tokens import RefreshTokenModel
from app.repos.postgres.tokens import RefreshTokenRepoPostgres
from app.exceptions.tokens import TokenNotFound, InvalidRefreshToken

# from app.env_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
# from app.env_config import settings

class AuthService:
    def __init__(self, repo: RefreshTokenRepoPostgres, access_expire_minutes: int, refresh_expire_days: int, secret_key: str, algorithm: str):
        self.repo = repo
        self.refresh_expire_days = refresh_expire_days
        self.access_expire_minutes = access_expire_minutes
        self.secret_key = secret_key
        self.algorithm = algorithm

    def _create_token(self, data: dict, expires_at: datetime, token_type: str, jti: str|None = None) -> str:
        to_encode = {
            # 'iss': ISSUER,
            # 'aud': AUDIENCE,
            # 'iat': datetime.now(),  
            'exp': expires_at, 
            'jti': jti or str(uuid4()),    
            'scope': token_type,                
            **data 
        }
        return encode(to_encode, self.secret_key, algorithm=self.algorithm)

    # @staticmethod
    def decode_token(self, token: str) -> dict:
        try:
            payload = decode(token, self.secret_key, algorithms=[self.algorithm])
        except (ExpiredSignatureError, InvalidTokenError):
            raise

        if not payload:
            raise InvalidRefreshToken()
        return payload


    def create_access_token(self, user_id: int) -> str:
        return self._create_token(
            data={'sub': str(user_id)}, 
            expires_at=datetime.now() + timedelta(minutes=self.access_expire_minutes), 
            token_type='access'
            )

    def create_refresh_token(self, user_id: int, expires_at: datetime, jti: str|None = None) -> str:
        return self._create_token(
            data={'sub': str(user_id)}, 
            expires_at=expires_at, 
            token_type='refresh', 
            jti=jti
            )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        return pwd_context.hash(password)
    

    async def add_refresh_token(self, user_id: int) -> str:
        jti = uuid4().hex
        expires_at = datetime.now() + timedelta(days=self.refresh_expire_days)

        new_token = RefreshTokenModel(
            id=jti,
            user_id=user_id,
            expires_at=datetime.now() + timedelta(days=self.refresh_expire_days)
        )

        await self.repo.create(new_token)
        return self.create_refresh_token(user_id, expires_at, jti)


    async def update_refresh_token(self, token: RefreshToken) -> RefreshToken:
        try:
            payload = self.decode_token(token)
        except (InvalidRefreshToken, ExpiredSignatureError, InvalidTokenError):
            raise
        
        user_id = int(payload.get('sub'))
        token_id = payload.get('jti')

        token_from_db = await self.repo.get_by_id(token_id)
        if not token_from_db or token_from_db.is_used or token_from_db.expires_at < datetime.now():
            raise InvalidRefreshToken()

        await self.repo.mark_as_used(token_from_db.id)

        new_jti = uuid4().hex
        expires_at = datetime.now() + timedelta(days=self.refresh_expire_days)
        new_refresh_token = self.create_refresh_token(user_id, expires_at, new_jti)
        new_access_token = self.create_access_token(user_id)

        new_token_row = RefreshTokenModel(
            id=new_jti,
            user_id=user_id,
            expires_at=expires_at
        )
        await self.repo.create(new_token_row)

        return RefreshToken(access_token=new_access_token, refresh_token=new_refresh_token)
    

    async def mark_refresh_token_as_used(self, refresh_token: str) -> bool:
        try:
            payload = self.decode_token(refresh_token)
        except (InvalidRefreshToken, ExpiredSignatureError, InvalidTokenError):
            raise
        
        token_id = payload.get('jti')
        
        try:
            return await self.repo.mark_as_used(token_id)
        except TokenNotFound:
            raise
