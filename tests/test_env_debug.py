import pytest
from httpx import AsyncClient

from app.constants.routes import DEBUG_ENV


@pytest.mark.asyncio
async def test_env_debug(client: AsyncClient) -> None:
    response = await client.get(DEBUG_ENV)
    assert response.status_code == 200
    assert "database_url" in response.json()
