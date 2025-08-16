from pymongo.collection import Collection

from app.repos.abstract.abstract_token_repo import AbstractRefreshTokenRepository
from app.schemas.tokens import RefreshToken, RefreshTokenFromDB


class RefreshTokenRepoMongo(AbstractRefreshTokenRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    async def create(self, token: RefreshToken) -> RefreshTokenFromDB:
        pass

    async def get_by_id(self, token_id: str) -> RefreshTokenFromDB|None:
        pass

    async def mark_as_used(self, token_id: str) -> bool:
        pass
        
