from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_track_repository
from app.schemas.track import Track, TrackCreate
from app.repositories.track import TrackRepository

router = APIRouter(prefix="/tracks", tags=["Tracks"])


@router.post("/", response_model=Track, status_code=status.HTTP_201_CREATED)
async def create_track(
    track: TrackCreate,
    repo: TrackRepository = Depends(get_track_repository)
) -> Track:
    created = await repo.get_or_create(track)
    return Track.model_validate(created)


@router.get("/{track_id}", response_model=Track)
async def get_track(
    track_id: str,
    repo: TrackRepository = Depends(get_track_repository)
) -> Track:
    found = await repo.get_by_id(track_id)
    if not found:
        raise HTTPException(status_code=404, detail="Track not found")
    return Track.model_validate(found)
