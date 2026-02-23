"""
JWT helpers — three token types, each with a distinct purpose claim.

Purpose claim prevents token misuse:
  - An email-verify token cannot be used as an access token
  - An access token cannot trigger email re-verification
  - A refresh token cannot access protected endpoints

Three different secrets add defence-in-depth:
  each key has a single job, compromise of one doesn't affect the others.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import jwt, JWTError

from app.config import get_settings

settings = get_settings()


# ─── Password helpers ───────────────────────────────────────────────────────


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ─── Token creation ──────────────────────────────────────────────────────────


def _make_token(subject: str, purpose: str, secret: str, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": subject, "purpose": purpose, "exp": expire}
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def create_access_token(email: str) -> str:
    return _make_token(
        email, "access", settings.JWT_SECRET_KEY,
        timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(email: str) -> str:
    return _make_token(
        email, "refresh", settings.JWT_REFRESH_SECRET,
        timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_email_token(email: str) -> str:
    """Verification link token — separate secret, TTL from settings."""
    return _make_token(
        email, "email_verify", settings.EMAIL_TOKEN_SECRET,
        timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS),
    )


# ─── Token decoding ───────────────────────────────────────────────────────────


def _decode(token: str, secret: str, expected_purpose: str) -> Optional[str]:
    """Return the email (sub) if the token is valid for *expected_purpose*, else None."""
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None

    if payload.get("purpose") != expected_purpose:
        return None

    return payload.get("sub")


def decode_access_token(token: str) -> Optional[str]:
    return _decode(token, settings.JWT_SECRET_KEY, "access")


def decode_refresh_token(token: str) -> Optional[str]:
    return _decode(token, settings.JWT_REFRESH_SECRET, "refresh")


def decode_email_token(token: str) -> Optional[str]:
    return _decode(token, settings.EMAIL_TOKEN_SECRET, "email_verify")
