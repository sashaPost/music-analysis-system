from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any

from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate
from app.api.deps import get_db_session, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=User,
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


@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: str, 
    db: AsyncSession = Depends(get_db_session)
) -> UserModel:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/summary")
async def get_user_summary(
    user_id: str, 
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get user summary with basic statistics"""
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    total_listens = len(user.listening_events)

    return {
        "user": User.model_validate(user),
        "stats": {
            "total_listening_events": total_listens,
            "member_since": user.created_at
        }
    }


@router.get("/me", tags=["Users"])
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
) -> dict:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "created_at": current_user.created_at.isoformat()
    }
