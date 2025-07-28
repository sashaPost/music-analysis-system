from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

from app.models.album import Album


class AlbumCRUD:
    @staticmethod
    async def get_or_create_by_name_and_artist(db: AsyncSession, name: str, artist_id: str) -> Album:
        stmt = select(Album).where(Album.name == name, Album.artist_id == artist_id)
        result = await db.execute(stmt)
        album = result.scalar_one_or_none()
        if album:
            return album

        new_album = Album(id=str(uuid4()), name=name, artist_id=artist_id)
        db.add(new_album)
        await db.flush()
        return new_album
