from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List, Any
import logging

from app.schemas.user import UserCreate, User as UserSchema
from app.services.spotify_ingestion_service import SpotifyIngestionService
from app.repositories.user import UserRepository
from app.repositories.artist import ArtistRepository
from app.repositories.album import AlbumRepository
from app.repositories.track import TrackRepository
from app.repositories.listening_event import ListeningEventRepository
from app.models.listening_event import ListeningEvent

logger = logging.getLogger(__name__)


class DataService:
    """Service for handling data operations"""
    def __init__(
        self,
        user_repo: UserRepository,
        artist_repo: ArtistRepository,
        album_repo: AlbumRepository,
        track_repo: TrackRepository,
        event_repo: ListeningEventRepository,
        ingestion: SpotifyIngestionService
    ):
        self.user_repo = user_repo
        self.artist_repo = artist_repo
        self.album_repo = album_repo
        self.track_repo = track_repo
        self.event_repo = event_repo
        self.ingestion = ingestion

    async def process_spotify_data(
            self,
            data: List[Dict[str, Any]],
            user_id: str,
    ) -> Dict[str, int]:
        """Process Spotify listening history data"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            user = await self.user_repo.create(
                UserCreate(id=user_id, username=user_id)
            )

        processed, skipped = 0, 0

        for item in data:
            if not self.ingestion.is_valid_record(item):
                skipped += 1
                continue

            try:
                artist = await self.artist_repo.get_or_create_by_name(
                    item["master_metadata_album_artist_name"]
                )
                album = await self.album_repo.get_or_create_by_name_and_artist(
                    item["master_metadata_album_album_name"], 
                    str(artist.id)
                )
                track_data, played_at, ms_played = self.ingestion.parse_record(
                    item,
                    str(artist.id),
                    str(album.id)
                )

                track = await self.track_repo.get_or_create(track_data)

                await self.event_repo.create_event(
                    str(user.id),
                    str(track.id),
                    played_at,
                    ms_played
                )
                processed += 1
            except Exception:
                logger.exception("Error processing item: %s", item)
                skipped += 1
        return {"processed": processed, "skipped": skipped}

    async def get_user_stats(self, user_id: str) -> dict[str, Any] | None:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            return None
        
        stats = await self.event_repo.get_user_stats(user_id)

        return {
            "user": UserSchema.model_validate(user),
            "stats": stats
        }
