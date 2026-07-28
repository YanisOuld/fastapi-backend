from backend.app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_is_not_plaintext() -> None:
    hashed = hash_password("supersecret")
    assert hashed != "supersecret"
    assert hashed.startswith("$2")  # bcrypt hash prefix


def test_verify_password_roundtrip() -> None:
    hashed = hash_password("supersecret")
    assert verify_password("supersecret", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_password_longer_than_72_bytes_does_not_crash() -> None:
    # bcrypt only considers the first 72 bytes; this must not raise.
    long_password = "a" * 200
    hashed = hash_password(long_password)
    assert verify_password(long_password, hashed) is True


def test_access_token_roundtrip() -> None:
    token = create_access_token("user-123")
    payload = decode_access_token(token)
    assert payload["sub"] == "user-123"
