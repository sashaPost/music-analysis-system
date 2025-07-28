from fastapi import status
from httpx import AsyncClient
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.constants.routes import API_PREFIX
from app.models.user import User

USERS_ENDPOINT = f"{API_PREFIX}/users"

pytestmark = pytest.mark.asyncio


async def test_get_current_user_info(
        client: AsyncClient,
        test_user_token: str
) -> None:
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = await client.get(f"{USERS_ENDPOINT}/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert "email" in data


async def test_read_user(
        client: AsyncClient,
        test_user: User,
        test_user_token: str
) -> None:
    headers = {"Authorization": f"Bearer {test_user_token}"}
    response = await client.get(f"{API_PREFIX}/users/{test_user.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_user.id)


async def test_get_user_summary_empty(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    test_user_token: str
) -> None:
    result = await db_session.execute(
        select(User).where(User.id == str(test_user.id))
    )
    test_user = result.scalar_one_or_none()
    assert test_user is not None

    response = await client.get(f"{USERS_ENDPOINT}/{str(test_user.id)}/summary")

    assert response.status_code == status.HTTP_200_OK
    summary = response.json()
    assert "user" in summary
    assert "stats" in summary
    assert summary["user"]["id"] == str(test_user.id)
    assert summary["stats"]["total_listening_events"] == 0
    assert "member_since" in summary["stats"]


async def test_read_user_not_found(
        client: AsyncClient, 
        test_user_token: str
) -> None:
    headers = {"Authorization": f"Bearer {test_user_token}"}
    fake_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    response = await client.get(f"{USERS_ENDPOINT}/{fake_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_user_summary_not_found(
        client: AsyncClient,
        test_user_token: str
) -> None:
    headers = {"Authorization": f"Bearer {test_user_token}"}
    fake_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    response = await client.get(
        f"{USERS_ENDPOINT}/{fake_id}/summary",
        headers=headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_create_user(client: AsyncClient) -> None:
    unique_email = f"user-{uuid.uuid4()}@example.com"

    new_user = {
        "username": "testuser",
        "email": unique_email
    }

    response = await client.post(f"{USERS_ENDPOINT}/", json=new_user)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == new_user["username"]
    assert data["email"] == new_user["email"]
    assert "id" in data
