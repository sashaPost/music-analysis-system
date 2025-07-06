from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate


class UserCRUD:
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    # def get_user_by_username(self, db: Session, username: str) -> Optional[UserModel]:
    #     return db.query(UserModel).filter(UserModel.username == username).first()
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
