import uuid

from backend.app.api.dependancies import DbSession
from backend.app.api.schemas.user import UserCreate, UserRead, UserUpdate
from backend.app.core.constant import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from backend.app.schemas.pagination import Page
from backend.app.services.user import UserService
from fastapi import APIRouter, Query, status

router = APIRouter()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, db: DbSession) -> UserRead:
    user = await UserService(db).create_user(data)
    return UserRead.model_validate(user)


@router.get("", response_model=Page[UserRead])
async def list_users(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> Page[UserRead]:
    users, total = await UserService(db).get_all(page=page, size=size)
    return Page.build(
        items=[UserRead.model_validate(u) for u in users],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: uuid.UUID, db: DbSession) -> UserRead:
    user = await UserService(db).get_by_id(user_id)
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: uuid.UUID, data: UserUpdate, db: DbSession) -> UserRead:
    user = await UserService(db).update_user(user_id, data)
    return UserRead.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, db: DbSession) -> None:
    await UserService(db).delete(user_id)
