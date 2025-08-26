from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, List
from uuid import UUID

from app.api.deps import (
    get_user_repository,
    get_current_user,
    get_user_service,
    get_music_provider
)
from app.domain.music.interfaces.music_data_provider import IMusicDataProvider
from app.models.user import User
from app.repositories.user import SQLAlchemyUserRepository
from app.schemas.track import Track
from app.schemas.user import UserCreate, User as UserOut 
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreate,
    repo: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> UserOut:
    """Create a new user"""
    created_user = await repo.create(user)
    return UserOut.model_validate(created_user)


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserOut:
    return current_user


@router.get("/{user_id:uuid}", response_model=UserOut)
async def read_user(
    user_id: UUID, 
    repo: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> UserOut:
    user = await repo.get_by_id(str(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(user)


@router.get("/{user_id:uuid}/summary")
async def get_user_summary(
    user_id: UUID,
    repo: SQLAlchemyUserRepository = Depends(get_user_repository),    
    # service: UserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """Get user summary with basic statistics"""
    # return await service.get_user_summary(str(user_id))
    user = await repo.get_by_id(str(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user": UserOut.model_validate(user),
        "stats": {
            "total_listening_events": len(user.listening_events),
            "member_since": user.created_at
        }
    }


@router.get("{user_id:uuid}/top-tracks")
async def get_user_top_tracks(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    provider: IMusicDataProvider = Depends(get_music_provider)
) -> List[Track]:
    return await service.get_user_top_tracks(str(user_id), provider)
