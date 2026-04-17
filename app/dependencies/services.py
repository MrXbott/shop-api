
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi import Depends

from app.db.postgres.db_postgres import get_session

from app.repos.postgres.users import UserRepoPostgres
from app.repos.postgres.roles import RoleRepoPostgres
from app.repos.postgres.tokens import RefreshTokenRepoPostgres
from app.repos.postgres.sessions import SessionRepoPostgres
from app.repos.postgres.products import ProductRepoPostgres
from app.repos.postgres.categories import CategoryRepoPostgres
from app.repos.postgres.orders import OrderRepoPostgres

from app.services.users import UserService
from app.services.auth import AuthService
from app.services.products import ProductService
from app.services.categories import CategoryService
from app.services.orders import OrderService

from app.env_config import settings


REPO_MAP = {
    'postgres': {
        'refresh_token_repo': RefreshTokenRepoPostgres,
        'session_repo': SessionRepoPostgres,
        'user': UserRepoPostgres,
        'role': RoleRepoPostgres,
        'product': ProductRepoPostgres,
        'category': CategoryRepoPostgres,
        'order': OrderRepoPostgres
    },
}

def make_repository_factory(repo_name: str):
    repo_cls = REPO_MAP[settings.db_engine][repo_name]
    async def get_repo(session: AsyncSession = Depends(get_session)):
        return repo_cls(session)
    return get_repo

get_token_repo = make_repository_factory('refresh_token_repo')
get_session_repo = make_repository_factory('session_repo')
get_user_repo = make_repository_factory('user')
get_role_repo = make_repository_factory('role')
get_product_repo = make_repository_factory('product')
get_category_repo = make_repository_factory('category')
get_order_repo = make_repository_factory('order')


def get_user_service(user_repo = Depends(get_user_repo), role_repo = Depends(get_role_repo)) -> UserService:
    return UserService(user_repo, role_repo)

def get_auth_service(session_repo = Depends(get_session_repo), token_repo = Depends(get_token_repo), user_service = Depends(get_user_service)) -> AuthService:
    return AuthService(token_repo=token_repo,
                       session_repo=session_repo,
                       user_service=user_service,
                       access_expire_minutes=settings.access_token_expire_minutes,
                       refresh_expire_days=settings.refresh_token_expire_days,
                       session_lifetime_days=settings.session_lifetime_days,
                       secret_key=settings.secret_key,
                       algorithm=settings.algorithm
                       )

def get_product_service(repo = Depends(get_product_repo)) -> ProductService:
    return ProductService(repo)

def get_category_service(repo = Depends(get_category_repo)) -> CategoryService:
    return CategoryService(repo)

def get_order_service(repo = Depends(get_order_repo)) -> OrderService:
    return OrderService(repo)
