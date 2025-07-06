from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class ArtistBase(BaseModel):
    name: str
    genres: Optional[List[str]] = []
    popularity: Optional[int] = 0
    followers: Optional[int] = 0


class ArtistCreate(ArtistBase):
    id: str


class Artist(ArtistBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
