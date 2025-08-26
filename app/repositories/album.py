from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.album_crud import AlbumCRUD
from app.models.album import Album


class AlbumRepository(ABC):
    @abstractmethod
    async def get_or_create_by_name_and_artist(
        self,
        name: str,
        artist_id: str
    ) -> Album:
        pass


class SQLAlchemyAlbumRepository(AlbumRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.crud = AlbumCRUD()
        self.session = session

    async def get_or_create_by_name_and_artist(
        self,
        name: str,
        artist_id: str
    ) -> Album:
        return await self.crud.get_or_create_by_name_and_artist(
            self.session, 
            name, 
            artist_id
        )
