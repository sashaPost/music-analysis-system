from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List, Any
from datetime import datetime
import logging

from app.models import User, Track, Artist
from app.models.listening_event import ListeningEvent
from app.schemas.user import UserCreate
from app.crud.user_crud import UserCRUD

logger = logging.getLogger(__name__)


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
        if user is None:
            user_create = UserCreate(id=user_id, username=user_id)
            user = await UserCRUD().create_user(db, user_create)


        processed_records = 0
        skipped_records = 0
        for record in data:
            if not self._is_valid_spotify_record(record):
                skipped_records += 1
                continue

            played_at_str = record.get("ts")
            if not played_at_str:
                skipped_records += 1
                continue

            try:
                played_at = datetime.fromisoformat(played_at_str.replace("Z", "+00:00"))
            except ValueError:
                skipped_records += 1
                continue

            track_name = record.get("master_metadata_track_name", "Unknown")
            artist_name = record.get("master_metadata_album_artist_name", "Unknown Artist")
            album_name = record.get("master_metadata_album_album_name", "Unknown Album")
            duration_ms = record.get("ms_played", 0)

            logger.debug(f"Processed track: {track_name}, by {artist_name}")

            # Simulate logic here. Replace with actual inserts/checks later.
            processed_records += 1

        await db.commit()
        return {"processed": processed_records, "skipped": skipped_records}

    def _is_valid_spotify_record(self, record: Dict[str, Any]) -> bool:
        return record.get("ts") is not None and record.get("ms_played", 0) > 0
    
    async def get_user_stats(
            self, 
            user_id: str, 
            db: AsyncSession
    ) -> dict[str, Any]:
        result = await db.execute(
            select(
                func.count(ListeningEvent.id),
                func.sum(ListeningEvent.duration_ms),
                func.min(ListeningEvent.played_at),
                func.max(ListeningEvent.played_at)
            ).where(ListeningEvent.user_id == user_id)
        )
        total_count, total_duration, first_play, last_play = result.one_or_none() or (0, 0, None, None)
        return {
        "total_listens": total_count,
        "total_played_ms": total_duration,
        "first_played": first_play,
        "last_played": last_play
    }
