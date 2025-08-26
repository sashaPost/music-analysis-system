from typing import Any, Optional
import httpx
import base64

from app.config import Settings
from app.constants.spotify import SPOTIFY_API_BASE_URL, SPOTIFY_TOKEN_URL


class SpotifyClient:
    BASE_URL = SPOTIFY_API_BASE_URL
    TOKEN_URL = SPOTIFY_TOKEN_URL

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._access_token: Optional[str] = None

    async def _authenticate(self) -> None:
        client_id = self._settings.spotify_client_id
        client_secret = self._settings.spotify_client_secret
        credentials = f"{client_id}:{client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        async with httpx.AsyncClient() as client:
            resp = await client.post(self.TOKEN_URL, headers=headers, data=data)
            resp.raise_for_status()
            self._access_token = resp.json()["access_token"]

    async def get(
            self, 
            endpoint: str, 
            params: Optional[dict] = None
    ) -> dict[str, Any]:
        if not self._access_token:
            await self._authenticate()

        headers = {"Authorization": f"Bearer {self._access_token}"}
        async with httpx.AsyncClient(base_url=self.BASE_URL) as client:
            resp = await client.get(endpoint, headers=headers, params=params)
            resp.raise_for_status()
            json_data: dict[str, Any] = resp.json()
            return json_data
