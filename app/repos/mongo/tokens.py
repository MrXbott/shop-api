from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# from datetime import datetime

# from app.schemas.token import Token
from app.repos.abstract.abstract_token_repo import AbstractRefreshTokenRepository
# from app.db.postgres.models.tokens import RefreshToken


class RefreshTokenMongoRepo(AbstractRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

   
        
