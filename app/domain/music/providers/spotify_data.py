import httpx
from typing import List
from app.domain.music.interfaces.music_data_provider import IMusicDataProvider

from app.constants.spotify import SPOTIFY_API_BASE_URL
from app.models.user import User
from app.schemas.track import Track


class SpotifyMusicDataProvider(IMusicDataProvider):
    BASE_URL = SPOTIFY_API_BASE_URL

    def __init__(self, token: str):
        self.token = token

    async def _get(self, endpoint: str, params: dict | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{self.BASE_URL}{endpoint}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            return resp.json()

    async def get_user_top_tracks(self, user: User) -> List[Track]:
        # Normally: token = user.spotify_access_token
        data = await self._get("/me/top/tracks", params={"limit": 10})
        return [
            Track(
                id=item["id"],
                name=item["name"],
                artist=", ".join(artist["name"] for artist in item["artists"]),
            )
            for item in data.get("items", [])
        ]

    async def get_user_profile(self, user: User) -> dict:
        return await self._get("/me")

    async def process_listening_history(self, user: User, data: List[dict]) -> None:
        # You'd probably persist or enrich this data
        for track in data:
            print(f"[Listening] User {user.id} listened to {track['name']} by {track['artists'][0]['name']}")
