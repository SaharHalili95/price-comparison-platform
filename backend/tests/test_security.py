from datetime import timedelta

import pytest

from app.core import security
from app.core.security import create_access_token, create_refresh_token, decode_token


def test_access_token_round_trip():
    token, jti, _ = create_access_token(subject=7, role="admin")
    payload = decode_token(token)
    assert payload["sub"] == "7"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"
    assert payload["jti"] == jti


def test_refresh_token_type():
    token, _, _ = create_refresh_token(subject=7)
    assert decode_token(token)["type"] == "refresh"


def test_tampered_token_is_rejected():
    token, _, _ = create_access_token(subject=7, role="user")
    header, payload, signature = token.split(".")
    with pytest.raises(Exception):
        decode_token(f"{header}.{payload}.{signature[::-1]}")


def test_expired_token_is_rejected(monkeypatch):
    real_now = security._utcnow
    monkeypatch.setattr(security, "_utcnow", lambda: real_now() - timedelta(days=1))
    token, _, _ = create_access_token(subject=7, role="user")
    monkeypatch.setattr(security, "_utcnow", real_now)
    with pytest.raises(Exception):
        decode_token(token)
