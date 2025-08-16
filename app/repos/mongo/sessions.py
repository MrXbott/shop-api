from pymongo.collection import Collection

from app.repos.abstract.abstract_session_repo import AbstractSessionRepository
from app.schemas.tokens import RefreshToken, RefreshTokenFromDB


class SessionRepoMongo(AbstractSessionRepository):
    def __init__(self, collection: Collection):
        self.collection = collection