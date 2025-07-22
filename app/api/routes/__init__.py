from fastapi import APIRouter

from app.api.routes import users, tracks, debug, spotify, spotify_auth_provider


api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(tracks.router)
api_router.include_router(debug.router)
api_router.include_router(spotify.router)
api_router.include_router(spotify_auth_provider.router)
