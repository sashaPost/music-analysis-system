from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.playlist import Playlist
from app.schemas.playlist import PlaylistCreate


class PlaylistCRUD:
    @staticmethod
    async def get_playlist_by_id(db: AsyncSession, playlist_id: str) -> Playlist | None:
        result = await db.execute(select(Playlist).where(Playlist.id == playlist_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_playlist(db: AsyncSession, playlist_data: PlaylistCreate) -> Playlist:
        playlist = Playlist(**playlist_data.model_dump())
        db.add(playlist)
        await db.commit()
        await db.refresh(playlist)
        return playlist
