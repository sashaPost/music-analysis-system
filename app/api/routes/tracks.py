from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.track import Track as TrackModel
from app.schemas.track import Track, TrackCreate
from app.api.deps import get_db_session

router = APIRouter(prefix="/tracks", tags=["Tracks"])


@router.post("/", response_model=Track, status_code=201)
async def create_track(
    track: TrackCreate,
    db: AsyncSession = Depends(get_db_session)
) -> TrackModel:
    db_track = TrackModel(**track.model_dump())
    db.add(db_track)
    await db.commit()
    await db.refresh(db_track)
    return db_track


@router.get("/{track_id}", response_model=Track)
async def get_track(
    track_id: str, 
    db: AsyncSession = Depends(get_db_session)
) -> TrackModel:
    result = await db.execute(select(TrackModel).where(TrackModel.id == track_id))
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track
