import pytest
import respx
from httpx import Response

from app.config import Settings
from app.services.spotify import SpotifyService


@pytest.mark.asyncio
@respx.mock
async def test_get_featured_categories():
    token_route = respx.post("https://accounts.spotify.com/api/token").mock(
        return_value=Response(200, json={"access_token": "fake-token"})
    )
    categories_route = respx.get("https://api.spotify.com/v1/browse/categories").mock(
        return_value=Response(200, json={"categories": {"items": []}})
    )

    settings = Settings(spotify_client_id="id", spotify_client_secret="secret")
    service = SpotifyService(settings)
    result = await service.get_featured_categories()

    assert "categories" in result
    assert token_route.called
    assert categories_route.called
