from datetime import datetime
from uuid import uuid4
from typing import Any, Dict

from app.schemas.track import TrackCreate

class SpotifyIngestionService:
    """Handles parsing and validating raw Spotify JSON data"""
    def is_valid_record(self, record: Dict[str, Any]) -> bool:
        return bool(
            record.get("ts") and
            record.get("ms_played", 0) > 0 and
            record.get("master_metadata_track_name") and
            record.get("master_metadata_album_artist_name") and
            record.get("master_metadata_album_album_name")
        )
    
    def parse_record(
            self, 
            record: Dict[str, Any],
            artist_id: str,
            album_id: str
    ) -> tuple[TrackCreate, datetime, int]:
        played_at = datetime.fromisoformat(record["ts"].replace("Z", "+00:00"))
        ms_played = int(record["ms_played"])
        track_name = record["master_metadata_track_name"]

        track_data = TrackCreate(
            id=str(uuid4()),
            name=track_name,
            duration_ms=ms_played,
            artist_id=artist_id,
            album_id=album_id,
        )
        return track_data, played_at, ms_played
