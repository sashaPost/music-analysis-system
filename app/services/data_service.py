from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List, Any
from datetime import datetime
import logging
from uuid import uuid4

from app.crud.artist_crud import ArtistCRUD
from app.crud.album_crud import AlbumCRUD
from app.crud.track_crud import TrackCRUD
from app.crud.user_crud import UserCRUD
from app.models.listening_event import ListeningEvent
from app.schemas.track import TrackCreate
from app.schemas.user import UserCreate, User as UserSchema

logger = logging.getLogger(__name__)

artist_crud = ArtistCRUD()
album_crud = AlbumCRUD()
track_crud = TrackCRUD()


class DataService:
    """Service for handling data operations"""

    async def process_spotify_data(
            self,
            data: List[Dict[str, Any]],
            user_id: str,
            db: AsyncSession
    ) -> Dict[str, int]:
        """Process Spotify listening history data"""
        user = await UserCRUD().get_user_by_id(db, user_id)
        if not user:
            user_create = UserCreate(id=user_id, username=user_id)
            user = await UserCRUD().create_user(db, user_create)

        processed = 0
        skipped = 0

        for item in data:
            try:
                played_at = datetime.fromisoformat(item["ts"].replace("Z", "+00:00"))
                ms_played = int(item.get("ms_played", 0))
                track_name = item.get("master_metadata_track_name")
                artist_name = item.get("master_metadata_album_artist_name")
                album_name = item.get("master_metadata_album_album_name")

                if not track_name or not artist_name or not album_name or ms_played == 0:
                    skipped += 1
                    continue

                artist = await artist_crud.get_or_create_by_name(db, artist_name)

                album = await album_crud.get_or_create_by_name_and_artist(
                    db, album_name,
                    str(artist.id)
                )

                track_data = TrackCreate(
                    id=str(uuid4()),
                    name=track_name,
                    duration_ms=ms_played,
                    artist_id=str(artist.id),
                    album_id=str(album.id),
                )

                track = await track_crud.get_or_create_track(db, track_data)

                event = ListeningEvent(
                    user_id=user.id,
                    track_id=track.id,
                    played_at=played_at,
                    duration_ms=ms_played,
                    progress_ms=0,
                    skipped=False,
                )
                db.add(event)
                processed += 1
            except Exception:
                logger.exception("Error processing item: %s", item)
                skipped += 1
        await db.commit()
        return {"processed": processed, "skipped": skipped}

    def _is_valid_spotify_record(self, record: Dict[str, Any]) -> bool:
        return record.get("ts") is not None and record.get("ms_played", 0) > 0
    
    async def get_user_stats(
            self, 
            user_id: str, 
            db: AsyncSession
    ) -> dict[str, Any] | None:
        user = await UserCRUD().get_user_by_id(db, user_id)
        if user is None:
            return None
        
        result = await db.execute(
            select(
                func.count(ListeningEvent.id),
                func.sum(ListeningEvent.duration_ms),
                func.min(ListeningEvent.played_at),
                func.max(ListeningEvent.played_at)
            ).where(ListeningEvent.user_id == user_id)
        )
        
        total_count, total_duration, first_play, last_play = (
            result.one_or_none() or (0, 0, None, None)
        )
        
        return {
            "user": UserSchema.model_validate(user),
            "stats": {
                "total_listens": total_count,
                "total_played_ms": total_duration or 0,
                "first_played": first_play,
                "last_played": last_play
            }
        }