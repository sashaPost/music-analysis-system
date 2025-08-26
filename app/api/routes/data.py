from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Any
import json

from app.api.deps import (
    get_data_service,
    get_listening_event_repository,
    get_track_repository,
)
from app.repositories.listening_event import ListeningEventRepository
from app.repositories.track import TrackRepository
from app.schemas.track import Track
from app.schemas.listening_event import ListeningEvent
from app.services.data_service import DataService

router = APIRouter(prefix="/data", tags=["Data Upload"])


@router.post("/upload/spotify", status_code=status.HTTP_202_ACCEPTED)
async def upload_spotify_data(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    service: DataService = Depends(get_data_service)
) -> dict[str, Any]:
    if file.content_type != "application/json":
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. JSON required."
        )

    try:
        contents = await file.read()
        data = json.loads(contents.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Could not decode JSON.")

    result = await service.process_spotify_data(data, user_id)
    return {"message": "Data uploaded and processed", "details": result}


@router.get("/users/{user_id}/listening-history")
async def get_user_listening_history(
    user_id: str,
    limit: int = 100,
    offset: int = 0,
    repo: ListeningEventRepository = Depends(get_listening_event_repository)
) -> dict[str, Any]:
    events = await repo.get_user_listening_history(
        user_id,
        limit,
        offset
    )
    return {
        "user_id": user_id,
        "events": [ListeningEvent.model_validate(ev) for ev in events],
        "total": len(events),
        "limit": limit,
        "offset": offset
    }


@router.get("/users/{user_id}/stats")
async def get_user_stats(
    user_id: str,
    service: DataService = Depends(get_data_service)
) -> dict[str, Any]:
    result = await service.get_user_stats(user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.get("/tracks/{track_id}")
async def get_track(
    track_id: str,
    repo: TrackRepository = Depends(get_track_repository)
) -> Track:
    track = await repo.get_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return Track.model_validate(track)


@router.get("/artists/{artist_id}/tracks", response_model=list[Track])
async def get_artist_tracks(
    artist_id: str, 
    repo: TrackRepository = Depends(get_track_repository)
) -> list[Track]:
    tracks = await repo.get_by_artist_id(artist_id)
    return [Track.model_validate(track) for track in tracks]
