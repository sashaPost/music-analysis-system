import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, Mock

from app.crud.track_crud import TrackCRUD
from app.models.track import Track
from app.schemas.track import TrackCreate
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_track_by_id_found() -> None:
    track = Track(id="track1", name="Track 1")
    db: AsyncSession = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = track
    db.execute.return_value = mock_result

    result = await TrackCRUD.get_track_by_id(db, "track1")

    assert result == track
    db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_track_by_id_not_found() -> None:
    db: AsyncSession = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    result = await TrackCRUD.get_track_by_id(db, "missing")

    assert result is None


@pytest.mark.asyncio
async def test_get_tracks_by_artist() -> None:
    tracks = [Track(id="t1"), Track(id="t2")]
    db: AsyncSession = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = tracks
    db.execute.return_value = mock_result

    result = await TrackCRUD.get_tracks_by_artist(db, "artist123")

    assert result == tracks
    db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_track() -> None:
    track_data = TrackCreate(
        id=str(uuid4()),
        name="Test Track",
        duration_ms=180000,
        album_id=str(uuid4()),
        artist_id=str(uuid4()),
        preview_url=None
    )

    db: AsyncSession = AsyncMock()
    db.add = Mock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await TrackCRUD.create_track(db, track_data)

    db.add.assert_called_once()
    db.commit.assert_awaited()
    db.refresh.assert_awaited()
    assert result.name == track_data.name


@pytest.mark.asyncio
async def test_get_or_create_track_existing() -> None:
    track = Track(id="t1", name="Existing")
    db: AsyncSession = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = track
    db.execute.return_value = mock_result

    data = TrackCreate(
        id="t1",
        name="Existing",
        duration_ms=180000,
        album_id="album1",
        artist_id="artist1",
        preview_url=None
    )

    result = await TrackCRUD.get_or_create_track(db, data)

    assert result == track
    db.add.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_track_new(monkeypatch) -> None:
    created_track = Track(id="t2", name="Created Track")

    async def mock_create_track(db, data):
        return created_track

    monkeypatch.setattr(TrackCRUD, "create_track", mock_create_track)

    db: AsyncSession = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    data = TrackCreate(
        id="t2",
        name="Created Track",
        duration_ms=210000,
        album_id="albumX",
        artist_id="artistX",
        preview_url=None
    )

    result = await TrackCRUD.get_or_create_track(db, data)

    assert result == created_track
