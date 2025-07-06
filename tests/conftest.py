import pytest_asyncio
from typing import AsyncGenerator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.config import settings

TEST_DB_URL = settings.database_url + "_test"
engine_test = create_async_engine(TEST_DB_URL, echo=True)
SessionTest = async_sessionmaker(engine_test, expire_on_commit=False)


@pytest_asyncio.fixture()
async def test_db() -> AsyncGenerator[None, None]:
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine_test.dispose()


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionTest() as session:
        yield session



@pytest_asyncio.fixture()
async def client(test_db: None) -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        async with SessionTest() as session:
            yield session

    app.dependency_overrides[get_db] = _get_test_db
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
