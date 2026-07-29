import uuid

from backend.app.api.dependancies import CurrentUserId, DbSession
from backend.app.api.schemas.auth import LoginRequest, TokenResponse
from backend.app.api.schemas.user import UserRead
from backend.app.core.security import create_access_token
from backend.app.services.user import UserService
from fastapi import APIRouter

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: DbSession) -> TokenResponse:
    user = await UserService(db).authenticate(data.email, data.password)
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
async def me(db: DbSession, user_id: CurrentUserId) -> UserRead:
    user = await UserService(db).get_by_id(uuid.UUID(user_id))
    return UserRead.model_validate(user)
