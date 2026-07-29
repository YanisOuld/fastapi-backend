from backend.app.schemas.base import AppSchema
from pydantic import Field


class LoginRequest(AppSchema):
    email: str = Field(max_length=255)
    password: str = Field(max_length=128)


class TokenResponse(AppSchema):
    access_token: str
    token_type: str = "bearer"
