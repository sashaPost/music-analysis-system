from fastapi import APIRouter

from app.api.routes import (
    data,
    debug,
    spotify,
    spotify_auth_provider,
    tracks,
    users,
)


api_router = APIRouter()
api_router.include_router(debug.router)
api_router.include_router(data.router)
api_router.include_router(spotify.router)
api_router.include_router(spotify_auth_provider.router)
api_router.include_router(tracks.router)
api_router.include_router(users.router)
