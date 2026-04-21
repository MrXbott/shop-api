from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import settings
from app.models.base import Base


async_engine = create_async_engine(settings.database_url, echo=False)
async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with async_session_maker() as session:
        yield session

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

