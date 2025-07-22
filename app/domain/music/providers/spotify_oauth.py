import httpx
from urllib.parse import urlencode
from typing import Any

from app.config import settings
from app.constants.spotify import (
    SPOTIFY_AUTH_URL, 
    SPOTIFY_TOKEN_URL, 
    SPOTIFY_API_BASE_URL,
)
from app.domain.music.interfaces.music_provider import MusicProvider


class SpotifyOAuthService(MusicProvider):
    SCOPE = "user-read-private user-read-email"

    def get_login_url(self, state: str) -> str:
        params = {
            "client_id": settings.spotify_client_id,
            "response_type": "code",
            "redirect_uri": settings.spotify_redirect_uri,
            "scope": self.SCOPE,
            "state": state,
        }
        return f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> dict[str, Any]:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.spotify_redirect_uri,
            "client_id": settings.spotify_client_id,
            "client_secret": settings.spotify_client_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as client:
            resp = await client.post(SPOTIFY_TOKEN_URL, data=data, headers=headers)
            resp.raise_for_status()
            token_data: dict[str, Any] = resp.json()
            return token_data

    async def get_user_profile(self, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SPOTIFY_API_BASE_URL}/me", headers=headers)
            resp.raise_for_status()
            return dict(resp.json())
