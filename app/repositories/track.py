from abc import ABC, abstractmethod
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.track_crud import TrackCRUD
from app.schemas.track import TrackCreate
from app.models.track import Track as TrackModel


class TrackRepository(ABC):
    @abstractmethod
    async def get_or_create(self, track_data: TrackCreate) -> TrackModel:
        pass
    
    @abstractmethod
    async def get_by_id(self, track_id: str) -> TrackModel | None:
        pass

    @abstractmethod
    async def get_by_artist_id(self, artist_id: str) -> list[TrackModel]:
        pass


class SQLAlchemyTrackRepository(TrackRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.crud = TrackCRUD()
        self.session = session

    async def get_or_create(self, track_data: TrackCreate) -> TrackModel:
        return await self.crud.get_or_create_track(self.session, track_data)
    
    async def get_by_id(self, track_id: str) -> TrackModel | None:
        result = await self.session.execute(
            select(TrackModel).where(TrackModel.id == track_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_artist_id(self, artist_id: str) -> list[TrackModel]:
        result = await self.session.execute(
            select(TrackModel).where(TrackModel.artist_id == artist_id)
        )
        return list(result.scalars().all())
