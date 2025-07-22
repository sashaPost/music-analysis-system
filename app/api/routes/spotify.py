from fastapi import APIRouter, Depends
from app.services.spotify import SpotifyService
from app.config import Settings

router = APIRouter()

@router.get("/categories", tags=["Spotify"])
async def get_categories(settings: Settings = Depends(Settings)) -> dict:
    service = SpotifyService(settings)
    return await service.get_featured_categories()
