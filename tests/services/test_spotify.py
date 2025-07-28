from httpx import Response
import pytest
import respx

from app.config import settings
from app.constants.spotify import SPOTIFY_API_BASE_URL, SPOTIFY_TOKEN_URL
from app.services.spotify import SpotifyService


@pytest.mark.asyncio
@respx.mock
async def test_get_featured_categories() -> None:
    respx.post(SPOTIFY_TOKEN_URL).mock(
        return_value=Response(200, json={"access_token": "mock-token"})
    )

    respx.get(f"{SPOTIFY_API_BASE_URL}/browse/categories").mock(
        return_value=Response(200, json={
            "categories": {
                "items": [
                    {"id": "pop", "name": "Pop"},
                    {"id": "rock", "name": "Rock"}
                ]
            }
        })
    )

    service = SpotifyService(settings)
    response = await service.get_featured_categories()

    assert "categories" in response
    assert isinstance(response["categories"]["items"], list)
    assert len(response["categories"]["items"]) == 2
