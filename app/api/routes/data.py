from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.db.database import get_db
from app.services.data_service import DataService
from app.schemas.track import Track
from app.schemas.listening_event import ListeningEvent
from app.crud.track_crud import TrackCRUD
from app.crud.listening_event_crud import ListeningEventCRUD

router = APIRouter(prefix="/data", tags=["Data Upload"])
data_service = DataService()


@router.post("/upload/spotify", status_code=status.HTTP_202_ACCEPTED)
async def upload_spotify_data(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    db: AsyncSession = Depends(get_db)
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

    result = await data_service.process_spotify_data(data, user_id, db)
    return {"message": "Data uploaded and processed", "details": result}


@router.get("/users/{user_id}/listening-history")
async def get_user_listening_history(
    user_id: str,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    crud = ListeningEventCRUD()
    if not hasattr(crud, "get_user_listening_history"):
        raise HTTPException(
            status_code=500, 
            detail="Method get_user_listening_history not implemented."
        )

    events = await crud.get_user_listening_history(db, user_id, limit, offset)
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
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    if not hasattr(data_service, "get_user_stats"):
        raise HTTPException(
            status_code=500, 
            detail="Method get_user_stats not implemented in DataService."
        )
    return await data_service.get_user_stats(user_id, db)


@router.get("/tracks/{track_id}")
async def get_track(track_id: str, db: AsyncSession = Depends(get_db)) -> Track:
    track = await TrackCRUD().get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return Track.model_validate(track)


@router.get("/artists/{artist_id}/tracks")
async def get_artist_tracks(
    artist_id: str, 
    db: AsyncSession = Depends(get_db)
) -> list[Track]:
    crud = TrackCRUD()
    if not hasattr(crud, "get_tracks_by_artist"):
        raise HTTPException(
            status_code=500, 
            detail="Method get_tracks_by_artist not implemented."
        )

    tracks = await crud.get_tracks_by_artist(db, artist_id)
    return [Track.model_validate(track) for track in tracks]
