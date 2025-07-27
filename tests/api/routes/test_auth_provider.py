import pytest
from httpx import AsyncClient, Response
import respx

from app.constants.routes import API_PREFIX
from app.constants.spotify import SPOTIFY_API_BASE_URL, SPOTIFY_TOKEN_URL
from app.core.security import create_access_token
from app.models.user import User

LOGIN_URL = f"{API_PREFIX}/auth/login"
CALLBACK_URL = f"{API_PREFIX}/auth/spotify/callback"
ME_URL = f"{API_PREFIX}/users/me"


@pytest.mark.asyncio
async def test_auth_login_redirect(client: AsyncClient) -> None:
    response = await client.get(
        f"{LOGIN_URL}?provider=spotify",
        follow_redirects=False
    )
    assert response.status_code == 307
    assert "accounts.spotify.com" in response.headers["location"]


@pytest.mark.asyncio
@respx.mock
async def test_auth_callback_creates_user(client: AsyncClient) -> None:
    """Should exchange code and create user from Spotify profile"""
    respx.post(SPOTIFY_TOKEN_URL).mock(
        return_value=Response(200, json={
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "expires_in": 3600
        })
    )
    respx.get(f"{SPOTIFY_API_BASE_URL}/me").mock(
        return_value=Response(200, json={
            "id": "mock-spotify-id",
            "email": "test@example.com",
            "display_name": "Mock User"
        })
    )
    response = await client.get(f"{CALLBACK_URL}?code=test-code&state=dev-state")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "Mock User"


@pytest.mark.asyncio
async def test_get_current_user_authenticated(
    client: AsyncClient,
    test_user: User,
    test_user_token: str
) -> None:
    response = await client.get(
        ME_URL,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == test_user.id


@pytest.mark.asyncio
async def test_get_current_user_unauthenticated(client: AsyncClient) -> None:
    """Should return 401 when no token is provided"""
    response = await client.get(ME_URL)
    assert response.status_code == 401
