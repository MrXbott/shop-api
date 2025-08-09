
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi import Depends

from app.db.postgres.db_postgres import get_session
from app.db.mongo.db_mongo import get_mongo_collection_factory

from app.repos.mongo.users import UserRepoMongo
from app.repos.mongo.tokens import RefreshTokenRepoMongo
from app.repos.mongo.products import ProductRepoMongo
from app.repos.mongo.categories import CategoryRepoMongo
from app.repos.mongo.orders import OrderRepoMongo

from app.repos.postgres.users import UserRepoPostgres
from app.repos.postgres.tokens import RefreshTokenRepoPostgres
from app.repos.postgres.products import ProductRepoPostgres
from app.repos.postgres.categories import CategoryRepoPostgres
from app.repos.postgres.orders import OrderRepoPostgres

from app.services.users import UserService
from app.services.auth import AuthService
from app.services.products import ProductService
from app.services.categories import CategoryService
from app.services.orders import OrderService
from app.env_config import settings


def make_repository_factory(postgres_cls, mongo_cls, mongo_collection_name: str):
    get_mongo_collection_dep = get_mongo_collection_factory(mongo_collection_name)

    async def get_repository(
        session: AsyncSession = Depends(get_session),
        collection = Depends(get_mongo_collection_dep),
    ):
        if settings.use_db == 'postgres':
            return postgres_cls(session)
        return mongo_cls(collection)
    return get_repository

get_auth_repo = make_repository_factory(RefreshTokenRepoPostgres, RefreshTokenRepoMongo, 'tokens')
get_user_repo = make_repository_factory(UserRepoPostgres, UserRepoMongo, 'users')
get_product_repo = make_repository_factory(ProductRepoPostgres, ProductRepoMongo, 'products')
get_category_repo = make_repository_factory(CategoryRepoPostgres, CategoryRepoMongo, 'categories')
get_order_repo = make_repository_factory(OrderRepoPostgres, OrderRepoMongo, 'orders')

def get_auth_service(repo = Depends(get_auth_repo)) -> AuthService:
    return AuthService(repo=repo,
                       access_expire_minutes=settings.access_token_expire_minutes,
                       refresh_expire_days=settings.refresh_token_expire_days,
                       secret_key=settings.secret_key,
                       algorithm=settings.algorithm
                       )

def get_user_service(repo = Depends(get_user_repo)) -> UserService:
    return UserService(repo)

def get_product_service(repo = Depends(get_product_repo)) -> ProductService:
    return ProductService(repo)

def get_category_service(repo = Depends(get_category_repo)) -> CategoryService:
    return CategoryService(repo)

def get_order_service(repo = Depends(get_order_repo)) -> OrderService:
    return OrderService(repo)
