from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.domain.music.factory import get_provider
from app.db.database import get_db
from app.schemas.user import UserCreate
from app.schemas.token import TokenResponse
from app.core.security import create_access_token
from app.repositories.user import SQLAlchemyUserRepository
from app.api.deps import get_user_repository

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/login")
async def login(
    provider: str = Query(...), 
    state: str = "dev-state"
) -> RedirectResponse:
    try:
        service = get_provider(provider)
        login_url = service.get_login_url(state)
        return RedirectResponse(login_url)
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail=str(e)
        )


@router.get(
    "/{provider}/callback", 
    response_model=TokenResponse,
)
async def callback(
    provider: str, 
    code: str = Query(...),
    state: str = Query(...),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    try:
        service = get_provider(provider)
        tokens = await service.exchange_code(code)
        profile = await service.get_user_profile(tokens["access_token"])

        provider_user_id = profile["id"]
        email = profile.get("email", f"{provider_user_id}@{provider}.music")
        name = profile.get("display_name", provider_user_id)

        user = await user_repo.get_by_provider_user_id(
            provider, 
            provider_user_id
        )

        if not user:
            user_data = UserCreate(username=name, email=email)
            user = await user_repo.create_with_social_account(
                user_data=user_data,
                provider=provider,
                provider_user_id=provider_user_id,
                access_token=tokens["access_token"],
                refresh_token=tokens.get("refresh_token"),
                expires_in=tokens.get("expires_in"),
            )

        access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=timedelta(minutes=30)  
        )
        return TokenResponse(access_token=access_token, user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Callback error: {e}")
