"""Unit tests for password hashing and JWT token utilities."""
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("admin123")
    assert hashed != "admin123"
    assert verify_password("admin123", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_password_hash_is_salted():
    assert hash_password("admin123") != hash_password("admin123")


def test_token_roundtrip():
    token = create_access_token(user_id=42, email="user@example.com")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["email"] == "user@example.com"
    assert payload["exp"]
