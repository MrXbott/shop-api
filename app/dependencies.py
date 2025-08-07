
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

from app.db.db_postgres import get_session
from app.db.db_mongo import get_mongo_collection_factory

from app.repos.mongo.users import UserMongoRepo
from app.repos.mongo.tokens import RefreshTokenMongoRepo
from app.repos.mongo.products import ProductMongoRepo

from app.repos.postgres.users import UserPostgresRepo
from app.repos.postgres.tokens import RefreshTokenPostgresRepo
from app.repos.postgres.products import ProductPostgresRepo

from app.services.users import UserService
from app.services.auth import AuthService
from app.services.products import ProductService
# from app.db.mongo.client import get_mongo_collection
# from app.db.mongo.user_repo_mongo import MongoUserRepository
# from app.db.postgres.user_repo_postgres import PostgresUserRepository
# from app.db.postgres.session import get_session
from fastapi import Depends

USE_DB = os.getenv('USE_DB', 'postgres')

def make_repository_factory(mongo_cls, postgres_cls, collection_name: str):
    get_mongo_collection_dep = get_mongo_collection_factory(collection_name)

    async def get_repository(
        session: AsyncSession = Depends(get_session),
        collection = Depends(get_mongo_collection_dep),
    ):
        if USE_DB == 'postgres':
            return postgres_cls(session)
        return mongo_cls(collection)
    return get_repository

get_auth_repo = make_repository_factory(RefreshTokenMongoRepo, RefreshTokenPostgresRepo, 'tokens')
get_user_repo = make_repository_factory(UserMongoRepo, UserPostgresRepo, 'users')
get_product_repo = make_repository_factory(ProductMongoRepo, ProductPostgresRepo, 'products')

def get_auth_service(repo = Depends(get_auth_repo)) -> AuthService:
    return AuthService(repo)

def get_user_service(repo = Depends(get_user_repo)) -> UserService:
    return UserService(repo)

def get_product_service(repo = Depends(get_product_repo)) -> ProductService:
    return ProductService(repo)