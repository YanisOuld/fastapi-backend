from backend.app.api.routes import health, info
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(info.router, prefix="/info", tags=["info"])
