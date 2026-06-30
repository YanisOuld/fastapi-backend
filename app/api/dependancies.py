from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_id
from app.core.db import AsyncSessionLocal
from app.core.redis import get_redis


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Typed shortcuts — use these as route dependencies instead of raw Depends()
#   def my_route(db: DbSession, user_id: CurrentUserId): ...
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
RedisClient = Annotated[object, Depends(get_redis)]
