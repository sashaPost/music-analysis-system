import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.data_service import DataService
from app.models.user import User
from app.models.artist import Artist
from app.models.album import Album
from app.models.track import Track


@pytest.mark.asyncio
async def test_process_valid_spotify_data_creates_user_and_counts_records() -> None:
    mock_db = AsyncMock(spec=AsyncSession)
    mock_data = [{
        "ts": "2023-01-01T12:00:00Z",
        "master_metadata_track_name": "Test Track",
        "master_metadata_album_artist_name": "Test Artist",
        "master_metadata_album_album_name": "Test Album",
        "ms_played": 180000
    }]
    user_id = "test_user"

    fake_user = User(id=user_id, username="test_user")
    fake_artist = Artist(id="artist_123", name="Test Artist")
    fake_album = Album(id="album_456", name="Test Album", artist_id=fake_artist.id)
    fake_track = Track(
        id="track_789",
        name="Test Track",
        duration_ms=180000,
        artist_id=fake_artist.id,
        album_id=fake_album.id,
        created_at=None
    )

    with patch(
        "app.services.data_service.artist_crud.get_or_create_by_name",
        new=AsyncMock(return_value=fake_artist)
    ), \
        patch(
            "app.services.data_service.album_crud.get_or_create_by_name_and_artist",
            new=AsyncMock(return_value=fake_album)
        ), \
        patch(
            "app.services.data_service.track_crud.get_or_create_track",
            new=AsyncMock(return_value=fake_track)
        ), \
        patch("app.services.data_service.UserCRUD") as MockUserCRUD:
        
        MockUserCRUD.return_value.get_user_by_id = AsyncMock(return_value=None)
        MockUserCRUD.return_value.create_user = AsyncMock(return_value=fake_user)

        service = DataService()
        result = await service.process_spotify_data(mock_data, user_id, mock_db)

        assert result["processed"] == 1
        assert result["skipped"] == 0
        mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_invalid_data_skips_record() -> None:
    mock_db = AsyncMock(spec=AsyncSession)
    mock_data = [{"ts": "invalid-date"}]
    user_id = "test_user"

    with patch("app.services.data_service.UserCRUD") as MockUserCRUD:
        crud_instance = MockUserCRUD.return_value
        crud_instance.get_user_by_id = AsyncMock(return_value=AsyncMock())

        service = DataService()
        result = await service.process_spotify_data(mock_data, user_id, mock_db)

        assert result["processed"] == 0
        assert result["skipped"] == 1
        mock_db.commit.assert_awaited_once()
