from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None
    public: Optional[bool] = False
    collaborative: Optional[bool] = False
    total_tracks: Optional[int] = 0


class PlaylistCreate(PlaylistBase):
    id: str
    user_id: str


class Playlist(PlaylistBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
