# import httpx
# from typing import Any

# from app.clients.spotify import SpotifyClient
# from app.config import Settings
# from app.constants.spotify import SPOTIFY_API_BASE_URL


# class SpotifyService:
#     def __init__(self, settings: Settings):
#         self._client = SpotifyClient(settings)

#     async def get_featured_categories(self) -> dict[str, Any]:
#         return await self._client.get("/browse/categories")

#     async def get_user_profile(self, access_token: str) -> dict[str, Any]:
#         headers = {"Authorization": f"Bearer {access_token}"}
        
#         async with httpx.AsyncClient() as client:
#             resp = await client.get(f"{SPOTIFY_API_BASE_URL}/me", headers=headers)
#             resp.raise_for_status()
#             json_data: dict[str, Any] = resp.json()
#             return json_data
