from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Dict, Any
from uuid import UUID

from app.models.user import User
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
) -> User:
    """Create a new user"""
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserOut:
    return current_user


@router.get("/{user_id:uuid}", response_model=UserOut)
async def read_user(
    user_id: UUID, 
    db: AsyncSession = Depends(get_db_session)
) -> User:
    result = await db.execute(
        select(User)
        .where(User.id == str(user_id))
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
    user = (await db.scalars(
        select(User)
        .options(selectinload(User.listening_events))
        .where(User.id == str(user_id))
    )).first()

    # result = await db.execute(
    #     select(User)
    #     .options(selectinload(User.listening_events))
    #     .where(User.id == str(user_id))
    # )
    
    # # DEBUG:
    # row = result.fetchone()
    # print("ROW:", row)
    
    # user = result.scalars().first()
    # # user = result.scalar_one_or_none()   
    # # user = row[0] if row else None 

    # # TEMP:
    # # Fallback for test context identity mismatch
    # if user is None:
    #     row = result.first()
    #     if row:
    #         user = row[0]
    
    # DEBUG:
    print("LOADED USER:", user)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user": UserOut.model_validate(user),
        "stats": {
            "total_listening_events": len(user.listening_events),
            "member_since": user.created_at
        }
    }
