from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class TrackBase(BaseModel):
    name: str
    duration_ms: int
    popularity: Optional[int] = 0
    explicit: Optional[bool] = False

    acousticness: Optional[float] = None
    danceability: Optional[float] = None
    energy: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    loudness: Optional[float] = None
    speechiness: Optional[float] = None
    tempo: Optional[float] = None
    valence: Optional[float] = None


class TrackCreate(TrackBase):
    id: str
    artist_id: str
    album_id: str


class Track(TrackBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    album_id: str
    created_at: datetime
