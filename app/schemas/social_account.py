from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.social_account import SocialAccount


class SocialAccountBase(BaseModel):
    provider: str
    provider_user_id: str


class SocialAccountCreate(SocialAccountBase):
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class SocialAccountUpdate(SocialAccountBase):
    id: str
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None

    class Config:
        orm_mode = True
