"""
Unit tests for JWT token logic.

These tests never touch the database or any external service.
They verify the security guarantees our token system must provide:
  1. Tokens expire
  2. Wrong-purpose tokens are rejected
  3. Tampered tokens are rejected
  4. Password hashing works correctly
"""

from datetime import timedelta

import pytest
from jose import jwt

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_email_token,
    decode_access_token,
    decode_refresh_token,
    decode_email_token,
    _make_token,
)
from app.config import get_settings

settings = get_settings()


# ─── Password ─────────────────────────────────────────────────────────────────


def test_hash_password_not_plain():
    hashed = hash_password("secret")
    assert hashed != "secret"


def test_verify_password_correct():
    hashed = hash_password("correct")
    assert verify_password("correct", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("correct")
    assert verify_password("wrong", hashed) is False


# ─── Access token ─────────────────────────────────────────────────────────────


def test_access_token_roundtrip():
    token = create_access_token("user@example.com")
    assert decode_access_token(token) == "user@example.com"


def test_access_token_expired():
    # Create a token that expired 1 second ago
    token = _make_token("user@example.com", "access", settings.JWT_SECRET_KEY, timedelta(seconds=-1))
    assert decode_access_token(token) is None


def test_access_token_wrong_purpose_rejected():
    # An email token must NOT decode as an access token
    email_token = create_email_token("user@example.com")
    assert decode_access_token(email_token) is None


def test_access_token_tampered():
    token = create_access_token("user@example.com")
    tampered = token[:-5] + "XXXXX"
    assert decode_access_token(tampered) is None


# ─── Refresh token ────────────────────────────────────────────────────────────


def test_refresh_token_roundtrip():
    token = create_refresh_token("user@example.com")
    assert decode_refresh_token(token) == "user@example.com"


def test_access_token_not_accepted_as_refresh():
    access_token = create_access_token("user@example.com")
    assert decode_refresh_token(access_token) is None


# ─── Email verification token ─────────────────────────────────────────────────


def test_email_token_roundtrip():
    token = create_email_token("user@example.com")
    assert decode_email_token(token) == "user@example.com"


def test_email_token_expired():
    token = _make_token(
        "user@example.com", "email_verify", settings.EMAIL_TOKEN_SECRET, timedelta(seconds=-1)
    )
    assert decode_email_token(token) is None


def test_email_token_wrong_purpose_rejected():
    # An access token must NOT work as an email verification token
    access_token = create_access_token("user@example.com")
    assert decode_email_token(access_token) is None


def test_purpose_claim_present_in_payload():
    token = create_access_token("user@example.com")
    # Decode without verification just to inspect claims
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload["purpose"] == "access"
    assert payload["sub"] == "user@example.com"
