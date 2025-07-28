from datetime import datetime
from fastapi import status
from httpx import AsyncClient
import json
import pytest
from unittest.mock import AsyncMock, patch

from app.constants.routes import API_PREFIX
from app.models.user import User
from app.schemas.track import Track

VALID_CONTENT_TYPE = "application/json"
INVALID_CONTENT_TYPE = "text/csv"
UPLOAD_ENDPOINT = f"{API_PREFIX}/data/upload/spotify"
LISTENING_HISTORY_ENDPOINT = f"{API_PREFIX}/data/users/{{user_id}}/listening-history"
USER_STATS_ENDPOINT = f"{API_PREFIX}/data/users/{{user_id}}/stats"
TRACK_ENDPOINT = f"{API_PREFIX}/data/tracks/{{track_id}}"
ARTIST_TRACKS_ENDPOINT = f"{API_PREFIX}/data/artists/{{artist_id}}/tracks"

pytestmark = pytest.mark.asyncio


async def test_upload_valid_json(client: AsyncClient, test_user: User) -> None:
    payload = [{
        "ts": "2023-01-01T12:00:00Z",
        "master_metadata_track_name": "Track A",
        "master_metadata_album_artist_name": "Artist A",
        "master_metadata_album_album_name": "Album A",
        "ms_played": 120000
    }]
    files = {
        "file": ("example.json", json.dumps(payload), VALID_CONTENT_TYPE)
    }

    url = f"{UPLOAD_ENDPOINT}?user_id={test_user.id}"
    response = await client.post(url, files=files)

    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert "message" in data
    assert "details" in data
    assert isinstance(data["details"].get("processed"), int)
    assert isinstance(data["details"].get("skipped"), int)


async def test_upload_invalid_json(client: AsyncClient, test_user: User) -> None:
    files = {
        "file": ("bad.json", "{not-valid-json", VALID_CONTENT_TYPE)
    }

    url = f"{UPLOAD_ENDPOINT}?user_id={test_user.id}"
    response = await client.post(url, files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Could not decode JSON."


async def test_upload_wrong_content_type(client: AsyncClient, test_user: User) -> None:
    files = {
        "file": ("not_json.csv", "a,b,c\n1,2,3", INVALID_CONTENT_TYPE)
    }

    url = f"{UPLOAD_ENDPOINT}?user_id={test_user.id}"
    response = await client.post(url, files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid file type. JSON required."


async def test_get_listening_history_empty(client: AsyncClient, test_user: User) -> None:
    url = LISTENING_HISTORY_ENDPOINT.format(user_id=test_user.id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] == str(test_user.id)
    assert data["events"] == []
    assert data["total"] == 0
    assert data["limit"] == 100
    assert data["offset"] == 0


async def test_get_user_stats_empty(client: AsyncClient, test_user: User) -> None:
    url = USER_STATS_ENDPOINT.format(user_id=test_user.id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    stats = response.json()
    assert isinstance(stats, dict)


@patch("app.api.routes.data.TrackCRUD.get_track_by_id", new_callable=AsyncMock)
async def test_get_track_found(mock_get, client: AsyncClient) -> None:
    mock_get.return_value = Track.model_construct(
        id="track123",
        name="Cool Song",
        duration_ms=180000,
        artist_id="artist123",
        album_id="album123",
        created_at=datetime.utcnow()
    )

    response = await client.get(TRACK_ENDPOINT.format(track_id="track123"))
    assert response.status_code == 200
    assert response.json()["id"] == "track123"


@patch("app.api.routes.data.TrackCRUD.get_track_by_id", new_callable=AsyncMock)
async def test_get_track_not_found(mock_get, client: AsyncClient) -> None:
    mock_get.return_value = None

    response = await client.get(TRACK_ENDPOINT.format(track_id="missing"))
    assert response.status_code == 404
    assert response.json()["detail"] == "Track not found"


@patch("app.api.routes.data.TrackCRUD.get_tracks_by_artist", new_callable=AsyncMock)
async def test_get_artist_tracks(mock_get, client: AsyncClient) -> None:
    now = datetime.utcnow()
    mock_get.return_value = [
        Track.model_construct(
            id="track1",
            name="Song A",
            duration_ms=100000,
            artist_id="artistX",
            album_id="albumY",
            created_at=now
        ),
        Track.model_construct(
            id="track2",
            name="Song B",
            duration_ms=200000,
            artist_id="artistX",
            album_id="albumY",
            created_at=now
        )
    ]

    response = await client.get(ARTIST_TRACKS_ENDPOINT.format(artist_id="artistX"))
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["id"] == "track1"
