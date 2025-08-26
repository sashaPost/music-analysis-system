from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.routes import AUTH_TOKEN_URL
from app.domain.music.factory import get_provider
from app.domain.music.interfaces.music_provider import IMusicProvider
from app.db.database import get_db
from app.models.user import User
from app.repositories.user import SQLAlchemyUserRepository, UserRepository
from app.repositories.artist import ArtistRepository, SQLAlchemyArtistRepository
from app.repositories.album import AlbumRepository, SQLAlchemyAlbumRepository
from app.repositories.track import SQLAlchemyTrackRepository, TrackRepository
from app.repositories.listening_event import (
    ListeningEventRepository, 
    SQLAlchemyListeningEventRepository,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.data_service import DataService
from app.services.spotify_ingestion_service import SpotifyIngestionService
from app.domain.music.interfaces.music_data_provider import IMusicDataProvider

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_TOKEN_URL)


# --- Core DB session ---
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


# --- Repository providers ---
async def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)

async def get_artist_repository(
    session: AsyncSession = Depends(get_db_session)
) -> SQLAlchemyArtistRepository:
    return SQLAlchemyArtistRepository(session)

async def get_album_repository(
    session: AsyncSession = Depends(get_db_session)
) -> SQLAlchemyAlbumRepository:
    return SQLAlchemyAlbumRepository(session)

async def get_track_repository(
    session: AsyncSession = Depends(get_db_session)
) -> SQLAlchemyTrackRepository:
    return SQLAlchemyTrackRepository(session)

async def get_listening_event_repository(
    session: AsyncSession = Depends(get_db_session)
) -> SQLAlchemyListeningEventRepository:
    return SQLAlchemyListeningEventRepository(session)


# --- Service providers ---
async def get_user_service(
    repo: UserRepository=Depends(get_user_repository)
) -> UserService:
    return UserService(repo)

async def get_data_service(
    user_repo: UserRepository = Depends(get_user_repository),
    artist_repo: ArtistRepository = Depends(get_artist_repository),
    album_repo: AlbumRepository = Depends(get_album_repository),
    track_repo: TrackRepository = Depends(get_track_repository),
    event_repo: ListeningEventRepository = Depends(get_listening_event_repository),
    ingestion: SpotifyIngestionService = Depends(lambda: SpotifyIngestionService())
) -> DataService:
    return DataService(
        user_repo=user_repo,
        artist_repo=artist_repo,
        album_repo=album_repo,
        track_repo=track_repo,
        event_repo=event_repo,
        ingestion=ingestion
    )


# --- Auth + Music provider ---
async def get_music_provider(request: Request) -> IMusicProvider:
    provider_name: str | None = request.query_params.get("provider")
    if not provider_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'provider' query parameter"
        )
    try:
        return get_provider(provider_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown provider: {provider_name}. Error: {str(e)}"
        )
    

async def get_music_data_provider(request: Request) -> IMusicDataProvider:
    provider = await get_music_provider(request)
    if not isinstance(provider, IMusicDataProvider):
        raise HTTPException(
            status_code=400,
            detail=f"Provider does not support music data interface"
        )
    return provider


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> User:
    user_id: str = AuthService().decode_token(token)
    user: User | None = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
