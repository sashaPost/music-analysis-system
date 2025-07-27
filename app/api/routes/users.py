from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Dict, Any
from uuid import UUID

from app.models.user import User as UserModel
from app.schemas.user import UserCreate, User as UserOut 
from app.api.deps import get_db_session, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db_session)
) -> UserModel:
    """Create a new user"""
    db_user = UserModel(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
) -> UserOut:
    return current_user


@router.get("/{user_id:uuid}", response_model=UserOut)
async def read_user(
    user_id: UUID, 
    db: AsyncSession = Depends(get_db_session)
) -> UserModel:
    result = await db.execute(
        select(UserModel)
        .where(UserModel.id == str(user_id))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id:uuid}/summary")
async def get_user_summary(
    user_id: UUID, 
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get user summary with basic statistics"""
    result = await db.execute(
        select(UserModel)
        .options(selectinload(UserModel.listening_events))
        .where(UserModel.id == str(user_id))
    )
    user = result.scalar_one_or_none()    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user": UserOut.model_validate(user),
        "stats": {
            "total_listening_events": len(user.listening_events),
            "member_since": user.created_at
        }
    }
