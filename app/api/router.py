from fastapi import APIRouter

from app.api.routes import health, info

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(info.router, prefix="/info", tags=["info"])

# Register feature routers here as you build them:
# from app.api.routes import users
# api_router.include_router(users.router, prefix="/users", tags=["users"])
