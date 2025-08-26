from abc import ABC, abstractmethod
from typing import Any


class IMusicProvider(ABC):
    @abstractmethod
    def get_login_url(self, state: str) -> str:
        """Generate the login URL for the music provider."""
        pass

    @abstractmethod
    async def exchange_code(self, code: str) -> dict[str, Any]:
        """Exchange the authorization code for an access token."""
        pass

    @abstractmethod
    async def get_user_profile(self, access_token: str) -> dict[str, Any]:
        """Fetch the user's profile information using the access token."""
        pass
    