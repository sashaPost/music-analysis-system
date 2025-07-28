import pytest
from httpx import AsyncClient, Response
from fastapi import status
from unittest.mock import AsyncMock, Mock, patch
from typing import Any
from datetime import datetime, timezone
from types import SimpleNamespace

from app.main import app
from app.constants.routes import API_PREFIX


@pytest.mark.anyio
@patch("app.api.routes.spotify_auth_provider.get_provider")
async def test_login_redirect_ok(mock_get_provider: Mock) -> None:
    mock_service = Mock()
    mock_service.get_login_url.return_value = "https://mock-login"
    mock_get_provider.return_value = mock_service

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response: Response = await ac.get(
            f"{API_PREFIX}/auth/login?provider=spotify"
        )

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == "https://mock-login"


@pytest.mark.anyio
@patch(
    "app.api.routes.spotify_auth_provider.create_access_token",
    return_value="mocked.jwt.token"
)
@patch("app.api.routes.spotify_auth_provider.UserCRUD")
@patch("app.api.routes.spotify_auth_provider.get_provider")
async def test_callback_success_creates_user_and_token(
    mock_get_provider: AsyncMock,
    mock_user_crud_cls: AsyncMock,
    mock_create_token: AsyncMock
) -> None:
    service_mock = AsyncMock()
    service_mock.exchange_code.return_value = {
        "access_token": "mock_access",
        "refresh_token": "mock_refresh",
        "expires_in": 3600
    }
    service_mock.get_user_profile.return_value = {
        "id": "mock_user_id",
        "email": "user@example.com",
        "display_name": "Mock User"
    }
    mock_get_provider.return_value = service_mock

    now = datetime.now(timezone.utc)
    mock_user = SimpleNamespace(
        id="user-id",
        username="Mock User",
        email="user@example.com",
        created_at=now,
        updated_at=now
    )

    user_crud_mock = AsyncMock()
    user_crud_mock.get_user_by_provider_user_id.return_value = None
    user_crud_mock.create_user_with_social_account.return_value = mock_user
    mock_user_crud_cls.return_value = user_crud_mock

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response: Response = await ac.get(
            f"{API_PREFIX}/auth/spotify/callback?code=abc123&state=dev-state"
        )

    assert response.status_code == 200, response.text
    data: dict[str, Any] = response.json()
    assert data["access_token"] == "mocked.jwt.token"
    assert data["user"]["username"] == "Mock User"
