import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, Mock

from app.crud.album_crud import AlbumCRUD
from app.models.album import Album
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_or_create_album_existing() -> None:
    album = Album(id="1", name="Existing Album", artist_id="artist1")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = album

    db: AsyncSession = AsyncMock()
    db.execute.return_value = mock_result

    result = await AlbumCRUD.get_or_create_by_name_and_artist(
        db,
        "Existing Album",
        "artist1"
    )

    db.execute.assert_called_once()
    assert result == album
    db.add.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_album_new() -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    db: AsyncSession = AsyncMock()
    db.execute.return_value = mock_result
    db.add = Mock()
    db.flush = AsyncMock()

    name = "New Album"
    artist_id = str(uuid4())

    result = await AlbumCRUD.get_or_create_by_name_and_artist(db, name, artist_id)

    assert result.name == name
    assert result.artist_id == artist_id
    db.add.assert_called_once()
    db.flush.assert_awaited()
