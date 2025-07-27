import datetime
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import api_router
# from app.api.routes import data, analysis, visualization


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from fastapi.routing import APIRoute
    print("📦 Registered routes:")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"{route.path} -> {route.name}")
    yield


app = FastAPI(
    title="Music Analysis System",
    description="Personal music preference analysis and recommendation system",
    version="0.1.0",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    return {
        "message": "Music Analysis System API", 
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "timestamp": str(datetime.datetime.now())
    }


app.include_router(api_router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug"
    )
