from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.artist import Artist
from app.schemas.artist import ArtistCreate


class ArtistCRUD:
    @staticmethod
    async def get_artist_by_id(db: AsyncSession, artist_id: str) -> Artist | None:
        result = await db.execute(select(Artist).where(Artist.id == artist_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_artist(db: AsyncSession, artist_data: ArtistCreate) -> Artist:
        artist = Artist(**artist_data.model_dump())
        db.add(artist)
        await db.commit()
        await db.refresh(artist)
        return artist
