from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta, timezone

from app.models.social_account import SocialAccount
from app.models.user import User
from app.schemas.user import UserCreate


class UserCRUD:
    @staticmethod
    async def get_user_by_provider_user_id(
        db: AsyncSession,
        provider: str,
        provider_user_id: str
    ) -> User | None:
        """
        Fetch a user by their social account provider and user ID.
        """
        result = await db.execute(
            select(User)
            .join(SocialAccount)
            .where(
                and_(
                    SocialAccount.provider == provider,
                    SocialAccount.provider_user_id == provider_user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user_with_social_account(
        db: AsyncSession,
        user_data: UserCreate,
        provider: str,
        provider_user_id: str,
        access_token: str,
        refresh_token: str | None = None,
        expires_in: int | None = None
    ) -> User:
        """
        Create a new user and their associated social account.
        """
        user = User(**user_data.model_dump())
        db.add(user)

        token_expires_at = None
        if expires_in:
            token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        account = SocialAccount(
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            user=user
        )
        db.add(account)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
