from fastapi import APIRouter
from app.api.routes import users, tracks
from app.api.routes import debug


api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(tracks.router)
api_router.include_router(debug.router)
