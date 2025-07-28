from asgi_lifespan import LifespanManager
import asyncio
from collections.abc import AsyncGenerator
from httpx import AsyncClient, ASGITransport
import pytest
import pytest_asyncio
from starlette.types import ASGIApp
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from typing import cast
import uuid

from app.api.deps import get_db_session
from app.config import settings
from app.crud.user_crud import UserCRUD
from app.db.database import Base, get_db
from app.main import app
from app.models.user import User
from app.schemas.user import UserCreate

TEST_DB_URL = settings.database_url + "_test"
engine_test = create_async_engine(TEST_DB_URL, echo=True)
TestSessionLocal = async_sessionmaker(engine_test, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Session-wide event loop for session-scoped async fixtures like prepare_database"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine_test.dispose()


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_db():
        yield db_session  

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_db_session] = _get_test_db

    transport = ASGITransport(app=cast(ASGIApp, app))   # type: ignore[arg-type]
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def test_user(db_session: AsyncSession) -> User:
    user_data = UserCreate(
        username=f"user-{uuid.uuid4().hex[:8]}",
        email=f"test-{uuid.uuid4()}@example.com"
    )
    user = await UserCRUD().create_user_with_social_account(
        db=db_session,
        user_data=user_data,
        provider="spotify",
        provider_user_id=str(uuid.uuid4()),
        access_token="token",
        refresh_token="refresh",
        expires_in=3600
    )
    await db_session.commit()
    await db_session.refresh(user, attribute_names=["listening_events"])
    return user


@pytest_asyncio.fixture()
async def test_user_token(test_user: User) -> str:
    from app.core.security import create_access_token
    from datetime import timedelta
    return create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(minutes=30)
    )
