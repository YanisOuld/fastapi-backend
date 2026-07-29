import pytest
from backend.app.core.config import settings
from httpx import AsyncClient

USERS = "/api/v1/users"
AUTH = "/api/v1/auth"


async def _create(client: AsyncClient, email: str, password: str = "supersecret"):
    return await client.post(USERS, json={"email": email, "password": password})


async def test_login_returns_bearer_token(db_client: AsyncClient) -> None:
    await _create(db_client, "login@example.com")
    resp = await db_client.post(
        f"{AUTH}/login", json={"email": "login@example.com", "password": "supersecret"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


async def test_login_wrong_password_is_401(db_client: AsyncClient) -> None:
    await _create(db_client, "wrongpw@example.com")
    resp = await db_client.post(
        f"{AUTH}/login", json={"email": "wrongpw@example.com", "password": "not-it-at-all"}
    )
    assert resp.status_code == 401
    assert "Incorrect email or password" in resp.json()["detail"]


async def test_login_unknown_email_is_401(db_client: AsyncClient) -> None:
    resp = await db_client.post(
        f"{AUTH}/login", json={"email": "ghost@example.com", "password": "supersecret"}
    )
    assert resp.status_code == 401


@pytest.fixture
def enforce_auth(monkeypatch: pytest.MonkeyPatch):
    # /me only means anything when the bearer token is actually validated.
    monkeypatch.setattr(settings, "BYPASS_AUTH", False)


async def test_me_returns_current_user(db_client: AsyncClient, enforce_auth: None) -> None:
    created = (await _create(db_client, "me@example.com")).json()
    token = (
        await db_client.post(
            f"{AUTH}/login", json={"email": "me@example.com", "password": "supersecret"}
        )
    ).json()["access_token"]

    resp = await db_client.get(f"{AUTH}/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "me@example.com"
    assert body["id"] == created["id"]


async def test_me_without_token_is_401(db_client: AsyncClient, enforce_auth: None) -> None:
    resp = await db_client.get(f"{AUTH}/me")
    assert resp.status_code == 401


async def test_me_with_garbage_token_is_401(db_client: AsyncClient, enforce_auth: None) -> None:
    resp = await db_client.get(f"{AUTH}/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401
