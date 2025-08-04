import jwt
from uuid import uuid4
from datetime import datetime, timedelta
from passlib.context import CryptContext

from env_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def create_token(data: dict, expires_at: datetime, token_type: str, jti: str|None = None) -> str:
    to_encode = {
        # 'iss': ISSUER,
        # 'aud': AUDIENCE,
        # 'iat': datetime.now(),  
        'exp': expires_at, 
        'jti': jti or str(uuid4()),    
        'scope': token_type,                
        **data 
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: int) -> str:
    return create_token(
        data={'sub': str(user_id)}, 
        expires_at=datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), 
        token_type='access'
        )


def create_refresh_token(user_id: int, expires_at: datetime, jti: str|None = None, ):
    return create_token(
        data={'sub': str(user_id)}, 
        expires_at=expires_at, 
        token_type='refresh', 
        jti=jti
        )

def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
