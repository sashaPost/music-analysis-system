from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.artist_crud import ArtistCRUD
from app.models.artist import Artist


class ArtistRepository(ABC):
    @abstractmethod
    async def get_or_create_by_name(self, name: str) -> Artist:
        """Fetch or create an artist by their name."""
        pass


class SQLAlchemyArtistRepository(ArtistRepository):
    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the ArtistCRUD."""
        self.crud = ArtistCRUD()
        self.session = session

    async def get_or_create_by_name(self, name: str) -> Artist:
        return await self.crud.get_or_create_by_name(self.session, name)
