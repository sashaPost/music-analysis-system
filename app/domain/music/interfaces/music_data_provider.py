from abc import ABC, abstractmethod
from typing import List

from app.models.user import User
from app.schemas.track import Track


class IMusicDataProvider(ABC):
    @abstractmethod
    async def get_user_top_tracks(self, user: User) -> List[Track]:
        """Fetch the user's top tracks from the music platform."""
        pass

    @abstractmethod
    async def get_user_profile(self, user: User) -> dict:
        """Fetch the user's profile information from the music data provider."""
        pass

    @abstractmethod
    async def process_listening_history(self, user: User, data: List[dict]) -> None:
        """Process the user's listening history data."""
        pass

    @abstractmethod
    async def get_featured_categories(self) -> dict:
        pass
