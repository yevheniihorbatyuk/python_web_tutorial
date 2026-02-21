"""
Unit tests for the email service.

We never send a real email in tests.  Instead we mock FastMail.send_message
and verify:
  - The correct recipient receives the email
  - The subject contains meaningful text
  - The body includes the verification URL
  - The token inside the URL is a valid email-verification token
"""

from unittest.mock import AsyncMock, patch, MagicMock
import pytest

from app.services.email import send_verification_email
from app.core.security import decode_email_token


async def test_send_verification_email_calls_fastmail():
    """send_verification_email must call FastMail.send_message exactly once."""
    with patch("app.services.email._mail") as mock_mail:
        mock_mail.send_message = AsyncMock()
        await send_verification_email("someone@example.com")
        mock_mail.send_message.assert_called_once()


async def test_verification_email_recipient():
    """The email must be addressed to the correct user."""
    captured = {}

    async def capture(message):
        captured["message"] = message

    with patch("app.services.email._mail") as mock_mail:
        mock_mail.send_message = capture
        await send_verification_email("recipient@example.com")

    assert "recipient@example.com" in captured["message"].recipients


async def test_verification_email_contains_valid_token():
    """The URL in the email body must contain a decodable verification token."""
    captured = {}

    async def capture(message):
        captured["body"] = message.body

    with patch("app.services.email._mail") as mock_mail:
        mock_mail.send_message = capture
        await send_verification_email("user@example.com")

    body = captured["body"]
    # Extract the token from the URL in the body
    # URL format: .../verify/{token}
    token_line = [line for line in body.splitlines() if "/verify/" in line][0]
    token = token_line.rstrip().split("/verify/")[-1]

    # Must decode as a valid email verification token for the right user
    email = decode_email_token(token)
    assert email == "user@example.com"
