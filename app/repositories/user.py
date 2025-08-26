from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_crud import UserCRUD
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        """Fetch a user by their ID."""
        pass

    @abstractmethod
    async def get_by_provider_user_id(self, provider: str, provider_user_id: str) -> User | None:
        """Fetch a user by provider + external user ID."""
        pass

    @abstractmethod
    async def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def create_with_social_account(
        self,
        user_data: UserCreate,
        provider: str,
        provider_user_id: str,
        access_token: str,
        refresh_token: str | None = None,
        expires_in: int | None = None
    ) -> User:
        """Create a user and link with external provider account."""
        pass


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud = UserCRUD()

    async def get_by_id(self, user_id: str) -> User | None:
        return await self.crud.get_user_by_id(self.session, user_id)
    
    async def get_by_provider_user_id(
        self, provider: str, provider_user_id: str
    ) -> User | None:
        return await self.crud.get_user_by_provider_user_id(
            self.session, provider, provider_user_id
        )

    async def create(self, user_data: UserCreate) -> User:
        return await self.crud.create_user(self.session, user_data)
    
    async def create_with_social_account(
        self,
        user_data: UserCreate,
        provider: str,
        provider_user_id: str,
        access_token: str,
        refresh_token: str | None = None,
        expires_in: int | None = None
    ) -> User:
        return await self.crud.create_user_with_social_account(
            db=self.session,
            user_data=user_data,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in
        )
