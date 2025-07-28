import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, Mock

from app.crud.artist_crud import ArtistCRUD
from app.models.artist import Artist
from app.schemas.artist import ArtistCreate
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_artist_by_id_found() -> None:
    artist = Artist(id="123", name="Test Artist")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = artist

    db: AsyncSession = AsyncMock()
    db.execute.return_value = mock_result

    result = await ArtistCRUD.get_artist_by_id(db, "123")

    db.execute.assert_called_once()
    assert result == artist


@pytest.mark.asyncio
async def test_get_artist_by_id_not_found() -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    db: AsyncSession = AsyncMock()
    db.execute.return_value = mock_result

    result = await ArtistCRUD.get_artist_by_id(db, "non-existent-id")

    assert result is None


@pytest.mark.asyncio
async def test_create_artist() -> None:
    artist_data = ArtistCreate(
        id=str(uuid4()), 
        name="New Artist", 
        genres=["pop"], 
        popularity=70, 
        followers=1000
    )

    db: AsyncSession = AsyncMock()
    db.add = Mock()  
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    result = await ArtistCRUD.create_artist(db, artist_data)

    db.add.assert_called_once()
    db.commit.assert_awaited()
    db.refresh.assert_awaited()
    assert result.name == artist_data.name


@pytest.mark.asyncio
async def test_get_or_create_by_name_existing() -> None:
    existing_artist = Artist(id="abc", name="Famous Artist")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_artist

    db: AsyncSession = AsyncMock()
    db.execute.return_value = mock_result

    result = await ArtistCRUD.get_or_create_by_name(db, "Famous Artist")

    assert result == existing_artist
    db.add.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_by_name_new() -> None:
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    db: AsyncSession = AsyncMock()
    db.execute.return_value = mock_result
    db.add = Mock()  # not awaited
    db.flush = AsyncMock()

    result = await ArtistCRUD.get_or_create_by_name(db, "New Artist")

    assert result.name == "New Artist"
    db.add.assert_called_once()
    db.flush.assert_awaited()
