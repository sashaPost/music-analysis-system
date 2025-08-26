from typing import List

from app.domain.music.interfaces.music_data_provider import IMusicDataProvider
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.track import Track


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_top_tracks(
            self, user_id: str, 
            data_provider: IMusicDataProvider
    ) -> List[Track]:
        """
        Fetch the user's top tracks from the specified music provider.
        
        Args:
            user_id (str): The ID of the user.
            provider (IMusicProvider): The music provider instance.
        
        Returns:
        """
        user: User | None = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")
        return await data_provider.get_user_top_tracks(user)
