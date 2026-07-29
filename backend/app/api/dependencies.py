from collections.abc import AsyncGenerator
from typing import Annotated

from backend.app.core.auth import get_current_user_id, verify_token
from backend.app.core.db import AsyncSessionLocal
from backend.app.core.redis import get_redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
RedisClient = Annotated[object, Depends(get_redis)]
RequireAuth = Depends(verify_token)
