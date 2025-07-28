import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.constants.routes import API_PREFIX
from app.models.album import Album
from app.models.artist import Artist
from app.models.track import Track

TRACKS_ENDPOINT = f"{API_PREFIX}/tracks"


@pytest.mark.asyncio
async def test_create_track(client: AsyncClient, db_session) -> None:
    track_id = str(uuid4())
    artist_id = str(uuid4())
    album_id = str(uuid4())

    artist = Artist(id=artist_id, name="Test Artist")
    album = Album(id=album_id, name="Test Album", artist_id=artist_id)
    db_session.add_all([artist, album])
    await db_session.commit()

    payload = {
        "id": track_id,
        "name": "API Test Track",
        "duration_ms": 240000,
        "artist_id": artist_id,
        "album_id": album_id,
        "preview_url": None
    }

    response = await client.post(f"{TRACKS_ENDPOINT}/", json=payload)

    assert response.status_code in (200, 201)
    data = response.json()
    assert data["id"] == track_id
    assert data["name"] == payload["name"]


@pytest.mark.asyncio
async def test_get_track_success(client: AsyncClient, db_session) -> None:
    artist_id = str(uuid4())
    album_id = str(uuid4())

    db_session.add_all([
        Artist(id=artist_id, name="Lookup Artist"),
        Album(id=album_id, name="Lookup Album", artist_id=artist_id)
    ])
    await db_session.commit()

    track = Track(
        id="track-get-1",
        name="Get Track",
        duration_ms=180000,
        artist_id=artist_id,
        album_id=album_id
    )
    db_session.add(track)
    await db_session.commit()

    response = await client.get(f"{TRACKS_ENDPOINT}/{track.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == track.id
    assert data["name"] == track.name


@pytest.mark.asyncio
async def test_get_track_not_found(client: AsyncClient) -> None:
    response = await client.get(f"{TRACKS_ENDPOINT}/non-existent-track-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Track not found"
