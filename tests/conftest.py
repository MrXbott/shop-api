import pytest
import pytest_asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

from app.models.base import Base  
from app.models.users import UserModel
from app.models.sessions import SessionModel
from app.models.tokens import RefreshTokenModel

load_dotenv()
POSTGRES_URL_TEST = os.getenv('POSTGRES_URL_TEST')

async_engine_test = create_async_engine(POSTGRES_URL_TEST, echo=False, poolclass=NullPool)


@pytest.fixture(scope='session', autouse=True)
async def prepare_test_db():
    async with async_engine_test.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

        await connection.execute(
            UserModel.__table__.insert(),
            [
                {
                    'first_name': 'Admin', 
                    'last_name': 'Adminov', 
                    'email': 'admin@example.com',
                    'password_hash': 'hashed_password',
                    'role': 'admin'
                },
                {
                    'first_name': 'User', 
                    'last_name': 'Userov', 
                    'email': 'user@example.com',
                    'password_hash': 'hashed_password',
                    'role': 'user'
                },
                {
                    'first_name': 'Ann', 
                    'last_name': 'A', 
                    'email': 'ann@example.com',
                    'password_hash': 'hashed_password',
                    'role': 'user'
                },
                {
                    'first_name': 'Bob', 
                    'last_name': 'B', 
                    'email': 'bob@example.com',
                    'password_hash': 'hashed_password',
                    'role': 'user'
                },
                {
                    'first_name': 'Ben', 
                    'last_name': 'B', 
                    'email': 'ben@example.com',
                    'password_hash': 'hashed_password',
                    'role': 'user'
                },
            ]
        )

    yield
    async with async_engine_test.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def test_session():
    async with async_engine_test.connect() as connection:
        trans = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)

        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()

