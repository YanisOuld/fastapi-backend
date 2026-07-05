from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.db import AsyncSessionLocal
from app.core.redis import get_redis


# Session-per-request unit of work: services only flush(), the whole request
# is one transaction, committed here on success and rolled back on error.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Typed shortcuts — use these as route dependencies instead of raw Depends()
#   def my_route(db: DbSession, user_id: CurrentUserId): ...
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
RedisClient = Annotated[object, Depends(get_redis)]
