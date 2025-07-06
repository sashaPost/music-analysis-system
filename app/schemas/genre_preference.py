from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserGenrePreferenceBase(BaseModel):
    genre: str
    preference_score: float = 0.0
    period: str


class UserGenrePreferenceCreate(UserGenrePreferenceBase):
    user_id: str


class UserGenrePreference(UserGenrePreferenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    calculated_at: datetime
