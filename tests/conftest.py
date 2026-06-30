from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.dependancies import get_db
from app.core.redis import get_redis
from app.main import app


def make_mock_db(raises: bool = False) -> AsyncMock:
    session = AsyncMock()
    if raises:
        session.execute.side_effect = Exception("DB unreachable")
    return session


def make_mock_redis(raises: bool = False) -> AsyncMock:
    redis = AsyncMock()
    if raises:
        redis.ping.side_effect = Exception("Redis unreachable")
    return redis


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    mock_session = make_mock_db()
    mock_redis = make_mock_redis()

    async def override_get_db():
        yield mock_session

    async def override_get_redis():
        return mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_db_down() -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield make_mock_db(raises=True)

    async def override_get_redis():
        return make_mock_redis()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_redis_down() -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield make_mock_db()

    async def override_get_redis():
        return make_mock_redis(raises=True)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
