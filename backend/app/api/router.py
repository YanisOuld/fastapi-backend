from backend.app.api.routes import auth, health, info, user
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(info.router, prefix="/info", tags=["info"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
