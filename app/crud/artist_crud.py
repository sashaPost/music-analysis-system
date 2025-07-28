from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

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

    @staticmethod
    async def get_or_create_by_name(db: AsyncSession, name: str) -> Artist:
        stmt = select(Artist).where(Artist.name == name)
        result = await db.execute(stmt)
        artist = result.scalar_one_or_none()
        if artist:
            return artist

        new_artist = Artist(id=str(uuid4()), name=name)
        db.add(new_artist)
        await db.flush()
        return new_artist
