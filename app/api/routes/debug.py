from fastapi import APIRouter
from typing import Any
from app.config import settings

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.get("/env")
async def get_env() -> dict[str, Any]:
    return settings.model_dump()
