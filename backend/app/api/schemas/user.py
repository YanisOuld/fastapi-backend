import uuid
from datetime import datetime

from backend.app.schemas.base import AppSchema
from pydantic import Field

# Note: `email: str` keeps the template dependency-free. For real validation,
# add `pydantic[email]` and switch these to `EmailStr`.


class UserCreate(AppSchema):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(AppSchema):
    email: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None


class UserRead(AppSchema):
    id: uuid.UUID
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
