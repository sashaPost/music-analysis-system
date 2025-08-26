from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_music_data_provider
from app.domain.music.interfaces.music_data_provider import IMusicDataProvider

router = APIRouter(prefix="/categories", tags=["Spotify"])

@router.get("")
async def get_categories(
    provider: IMusicDataProvider = Depends(get_music_data_provider)
) -> dict:
    try:
        return await provider.get_featured_categories()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch categories: {str(e)}"
        )
