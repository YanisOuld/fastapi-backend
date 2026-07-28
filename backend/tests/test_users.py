import uuid

from httpx import AsyncClient

BASE = "/api/v1/users"


async def _create(client: AsyncClient, email: str, password: str = "supersecret"):
    return await client.post(BASE, json={"email": email, "password": password})


async def test_create_user(db_client: AsyncClient) -> None:
    resp = await _create(db_client, "alice@example.com")
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["is_active"] is True
    assert uuid.UUID(body["id"])  # valid UUID
    # The password (or its hash) must never be exposed.
    assert "password" not in body
    assert "hashed_password" not in body


async def test_create_duplicate_email_conflicts(db_client: AsyncClient) -> None:
    await _create(db_client, "dup@example.com")
    resp = await _create(db_client, "dup@example.com", password="another12")
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


async def test_password_too_short_is_rejected(db_client: AsyncClient) -> None:
    resp = await _create(db_client, "short@example.com", password="short")
    assert resp.status_code == 422


async def test_list_users_paginated(db_client: AsyncClient) -> None:
    for i in range(3):
        await _create(db_client, f"user{i}@example.com")

    resp = await db_client.get(BASE, params={"page": 1, "size": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 3
    assert body["page"] == 1
    assert body["size"] == 2
    assert body["pages"] == 2
    assert len(body["items"]) == 2


async def test_get_user(db_client: AsyncClient) -> None:
    created = (await _create(db_client, "get@example.com")).json()
    resp = await db_client.get(f"{BASE}/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["email"] == "get@example.com"


async def test_get_unknown_user_returns_404(db_client: AsyncClient) -> None:
    resp = await db_client.get(f"{BASE}/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_update_user(db_client: AsyncClient) -> None:
    created = (await _create(db_client, "update@example.com")).json()
    resp = await db_client.patch(
        f"{BASE}/{created['id']}",
        json={"email": "renamed@example.com", "is_active": False},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "renamed@example.com"
    assert body["is_active"] is False


async def test_delete_user(db_client: AsyncClient) -> None:
    created = (await _create(db_client, "delete@example.com")).json()
    resp = await db_client.delete(f"{BASE}/{created['id']}")
    assert resp.status_code == 204

    resp = await db_client.get(f"{BASE}/{created['id']}")
    assert resp.status_code == 404
