"""
02. Email Verification Tokens: Security Evolution
=================================================

The CSV task: "explain why an email link without a timestamp is a bad idea."
This file demonstrates the evolution from insecure to secure token design.

Self-contained — no external services needed.
Run: python 02_email_verification_tokens.py

Key lesson: A link in an email is just a URL. If that URL doesn't expire,
anyone who gets it (forwarded email, email logs, server logs, browser history)
can use it indefinitely.
"""

import uuid
import time
import hashlib
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

# ============================================================
# APPROACH 1: UUID token (no expiry)
# ============================================================
"""
Many tutorials do this. It looks simple and works... until it doesn't.

Problem: The link https://example.com/verify?token=abc-uuid-here
is valid forever. If someone finds it 6 months later (in an
email backup, in server logs, via phishing), they can use it.
"""

# Fake token storage (in real app: database column verification_token)
_token_store: dict[str, str] = {}  # token → email


def generate_uuid_token(email: str) -> str:
    """Generate a UUID verification token with NO expiry."""
    token = str(uuid.uuid4())
    _token_store[token] = email
    return token


def verify_uuid_token(token: str) -> str | None:
    """Verify UUID token. Returns email if valid, None if not found."""
    return _token_store.get(token)


def demonstrate_uuid_token():
    print("APPROACH 1: UUID token (no expiry)")
    print("-" * 40)
    token = generate_uuid_token("alice@example.com")
    print(f"Generated token: {token[:20]}...")
    print(f"Link: https://example.com/verify?token={token[:20]}...")

    # Works immediately
    email = verify_uuid_token(token)
    print(f"Verified immediately: {email}")

    # Works 1 year later (simulated)
    print("\n[1 year later — token still in DB]")
    email = verify_uuid_token(token)
    print(f"Token still valid: {email}")
    print()
    print("VULNERABILITY: Token never expires.")
    print("→ Email leaked in a breach 1 year ago? Attacker still has access.\n")


# ============================================================
# APPROACH 2: JWT token without expiry
# ============================================================
"""
Better: JWT is self-contained (no database lookup), cryptographically
signed (cannot be forged). But still no expiry.
"""

SECRET = "some-secret-key"
ALGORITHM = "HS256"


def generate_jwt_no_expiry(email: str) -> str:
    """Generate a JWT verification token with NO expiry."""
    payload = {
        "sub": email,
        "purpose": "email_verify",
        # No "exp" field!
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def verify_jwt_no_expiry(token: str) -> str | None:
    """Verify JWT token. Returns email if valid."""
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def demonstrate_jwt_no_expiry():
    print("APPROACH 2: JWT token without expiry")
    print("-" * 40)
    token = generate_jwt_no_expiry("alice@example.com")
    print(f"JWT: {token[:40]}...")

    email = verify_jwt_no_expiry(token)
    print(f"Verified: {email}")

    # Attempt forgery
    fake_token = token[:-4] + "XXXX"
    result = verify_jwt_no_expiry(fake_token)
    print(f"Forged token rejected: {result is None}")

    print()
    print("IMPROVEMENT: Can't be forged (cryptographic signature).")
    print("REMAINING VULNERABILITY: Still doesn't expire.\n")


# ============================================================
# APPROACH 3: JWT with expiry + purpose claim (CORRECT)
# ============================================================
"""
This is what contacts_api uses.

Key additions:
1. "exp" claim: token expires after 24 hours
2. "purpose" claim: prevents an access token from being used
   as a verification token (different secrets help too, but
   purpose claim adds an explicit check)
"""

ACCESS_SECRET = "access-token-secret-do-not-reuse"
EMAIL_SECRET = "email-token-secret-different-from-access"


def create_email_verification_token(email: str, hours: int = 24) -> str:
    """Create a secure, time-limited email verification token."""
    expire = datetime.now(timezone.utc) + timedelta(hours=hours)
    payload = {
        "sub": email,
        "purpose": "email_verify",   # critical: prevents token confusion
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, EMAIL_SECRET, algorithm=ALGORITHM)


def verify_email_token(token: str) -> str:
    """
    Verify email token. Returns email if valid.
    Raises ValueError if expired, invalid, or wrong purpose.
    """
    try:
        payload = jwt.decode(token, EMAIL_SECRET, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e

    if payload.get("purpose") != "email_verify":
        raise ValueError("Token has wrong purpose (not an email verification token)")

    email = payload.get("sub")
    if not email:
        raise ValueError("Token missing subject")

    return email


def create_access_token(user_id: int) -> str:
    """Simulate an access token (Module 12 pattern)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": user_id, "type": "access", "exp": expire}
    return jwt.encode(payload, ACCESS_SECRET, algorithm=ALGORITHM)


def demonstrate_correct_approach():
    print("APPROACH 3: JWT with expiry + purpose claim (Correct)")
    print("-" * 40)

    # Normal flow
    token = create_email_verification_token("alice@example.com")
    email = verify_email_token(token)
    print(f"Valid token verified: {email}")

    # Expired token
    expired_token = create_email_verification_token("alice@example.com", hours=-1)
    try:
        verify_email_token(expired_token)
    except ValueError as e:
        print(f"Expired token rejected: {e}")

    # Access token used as email token (purpose mismatch)
    access_token = create_access_token(user_id=42)
    try:
        # Use ACCESS_SECRET instead of EMAIL_SECRET — would fail on signature
        # But let's show the purpose check even if same secret was used:
        payload = jwt.decode(access_token, ACCESS_SECRET, algorithms=[ALGORITHM])
        # Manually check purpose:
        if payload.get("purpose") != "email_verify" and payload.get("type") != "email_verify":
            raise ValueError("Token has wrong purpose")
    except Exception as e:
        print(f"Access token rejected as email token: {type(e).__name__}")

    print()
    print("SECURE BECAUSE:")
    print("  ✅ Cryptographically signed — cannot be forged")
    print("  ✅ Expires after 24 hours — leaked link becomes worthless")
    print("  ✅ Purpose claim — access tokens cannot verify emails")
    print("  ✅ Different secret — extra layer if purpose check is bypassed")


# ============================================================
# COMPARISON SUMMARY
# ============================================================

def print_comparison():
    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print(f"{'Approach':<25} {'Forgeable':<12} {'Expires':<10} {'DB needed':<12}")
    print("-" * 60)
    print(f"{'UUID token':<25} {'Yes (guess)':<12} {'No':<10} {'Yes':<12}")
    print(f"{'JWT no expiry':<25} {'No':<12} {'No':<10} {'No':<12}")
    print(f"{'JWT + exp + purpose':<25} {'No':<12} {'Yes':<10} {'No':<12}")
    print()
    print("Verdict: JWT + exp + purpose is the standard production approach.")
    print("Used in: contacts_api/app/core/security.py")


if __name__ == "__main__":
    print("Email Verification Token Security Demo")
    print("=" * 60)
    print()
    demonstrate_uuid_token()
    demonstrate_jwt_no_expiry()
    demonstrate_correct_approach()
    print_comparison()
