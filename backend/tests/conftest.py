import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import asyncpg
import pytest_asyncio
from backend.app.api.dependencies import get_db
from backend.app.core.config import settings
from backend.app.core.redis import get_redis
from backend.app.main import app
from backend.app.models import Base
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool


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


# --------------------------------------------------------------------------- #
# Real-database fixtures (Postgres)                                            #
#                                                                             #
# Tests run against a dedicated `<db>_test` database so dev data is never      #
# touched. Each test runs inside a transaction that is rolled back at the end, #
# so tests stay isolated and leave no rows behind.                            #
# --------------------------------------------------------------------------- #

# Dedicated test database: TEST_DATABASE_URL env override, else the configured
# database name with a `_test` suffix.
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or (
    settings.DATABASE_URL.rsplit("/", 1)[0]
    + "/"
    + settings.DATABASE_URL.rsplit("/", 1)[1]
    + "_test"
)


async def _ensure_test_database() -> None:
    """Create the test database if it does not exist yet."""
    server = settings.DATABASE_URL.replace("+asyncpg", "").rsplit("/", 1)[0]
    db_name = TEST_DATABASE_URL.rsplit("/", 1)[1]
    conn = await asyncpg.connect(f"{server}/postgres")
    try:
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", db_name)
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
    finally:
        await conn.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    await _ensure_test_database()
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Bind the session to a single connection wrapped in an outer transaction;
    # rolling that back after the test discards everything the test wrote.
    connection = await engine.connect()
    transaction = await connection.begin()
    session = async_sessionmaker(bind=connection, expire_on_commit=False)()
    try:
        yield session
    finally:
        await session.close()
        # A failed statement (e.g. a unique-violation) already aborts the
        # transaction, so only roll back if it is still active.
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()
        await engine.dispose()


@pytest_asyncio.fixture
async def db_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client wired to the real transactional session above."""

    async def override_get_db():
        yield db_session

    async def override_get_redis():
        return make_mock_redis()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
