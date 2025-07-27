from fastapi import APIRouter
from app.services.spotify import SpotifyService
from app.config import settings

router = APIRouter(prefix="/categories", tags=["Spotify"])

@router.get("")
async def get_categories() -> dict:
    return await SpotifyService(settings).get_featured_categories()
