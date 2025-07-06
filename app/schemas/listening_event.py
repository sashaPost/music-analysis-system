from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ListeningEventBase(BaseModel):
    played_at: datetime
    duration_ms: int
    progress_ms: int
    skipped: Optional[bool] = False
    context_type: Optional[str] = None
    context_id: Optional[str] = None


class ListeningEventCreate(ListeningEventBase):
    user_id: str
    track_id: str


class ListeningEvent(ListeningEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    track_id: str
    created_at: datetime
