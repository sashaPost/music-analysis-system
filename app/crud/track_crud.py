from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Sequence

from app.models.track import Track
from app.schemas.track import TrackCreate


class TrackCRUD:
    @staticmethod
    async def get_track_by_id(db: AsyncSession, track_id: str) -> Track | None:
        result = await db.execute(select(Track).where(Track.id == track_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tracks_by_artist(
        db: AsyncSession, 
        artist_id: str
    ) -> Sequence[Track]:
        result = await db.execute(select(Track)
                                  .where(Track.artist_id == artist_id))
        return result.scalars().all()

    @staticmethod
    async def create_track(db: AsyncSession, track_data: TrackCreate) -> Track:
        track = Track(**track_data.model_dump())
        db.add(track)
        await db.commit()
        await db.refresh(track)
        return track
