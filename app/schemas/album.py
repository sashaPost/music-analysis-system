from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class AlbumBase(BaseModel):
    name: str
    release_date: Optional[str] = None
    total_tracks: Optional[int] = 0
    album_type: Optional[str] = None


class AlbumCreate(AlbumBase):
    id: str
    artist_id: str


class Album(AlbumBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    artist_id: str
    created_at: datetime
