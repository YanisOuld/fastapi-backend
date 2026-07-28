from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    PROJECT_NAME: str = "FastAPI Template"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # Database (PostgreSQL + asyncpg)
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/dbname"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS — liste d'origins autorisées en prod (ex: ["https://myapp.com"])
    ALLOWED_ORIGINS: list[str] = ["https://localhost:8000"]

    # Security
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Auth — skips JWT verification, every request is treated as authenticated.
    # Convenient for local dev / early prototyping. Never allowed outside DEBUG.
    BYPASS_AUTH: bool = True

    @model_validator(mode="after")
    def _forbid_bypass_auth_outside_debug(self) -> "Settings":
        if self.BYPASS_AUTH and not self.DEBUG:
            raise ValueError(
                "BYPASS_AUTH=True is not allowed when DEBUG=False. "
                "Set BYPASS_AUTH=False before deploying outside local dev."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
