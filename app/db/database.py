from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from redis import Redis
from typing import AsyncGenerator, Generator
from app.config import settings

engine = create_async_engine(settings.database_url, echo=True)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


def get_redis() -> Generator[Redis, None, None]:
    """Redis dependency for FastAPI"""
    yield redis_client
