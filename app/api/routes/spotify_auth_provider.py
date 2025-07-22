from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.crud.user_crud import UserCRUD
from app.domain.music.factory import get_provider
from app.db.database import get_db
from app.schemas.user import UserCreate
from app.schemas.token import TokenResponse
from app.core.security import create_access_token

router = APIRouter()


@router.get("/auth/login", tags=["MusicAuth"])
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
        ) from e


@router.get(
    "/auth/{provider}/callback", 
    response_model=TokenResponse,
    tags=["MusicAuth"]
)
async def callback(
    provider: str, 
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db)
# ) -> JSONResponse:
) -> TokenResponse:
    try:
        service = get_provider(provider)
        tokens = await service.exchange_code(code)
        profile = await service.get_user_profile(tokens["access_token"])

        provider_user_id = profile["id"]
        email = profile.get("email", f"{provider_user_id}@{provider}.music")
        name = profile.get("display_name", provider_user_id)

        user_crud = UserCRUD()
        user = await user_crud.get_user_by_provider_user_id(
            db, 
            provider, 
            provider_user_id
        )

        if not user:
            user_data = UserCreate(username=name, email=email)
            user = await user_crud.create_user_with_social_account(
                db=db,
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

        # return JSONResponse({
        #     "user": {
        #         "id": user.id,
        #         "email": user.email,
        #         "username": user.username,
        #     },
        #     "provider": provider,
        #     "provider_user_id": provider_user_id
        # })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Callback error: {e}")
