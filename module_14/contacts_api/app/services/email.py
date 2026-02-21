"""
Email service using FastAPI-Mail.

FastAPI-Mail wraps aiosmtplib so sending happens in the same async event
loop — no thread pool, no blocking.  For dev we point at MailHog; for
production we swap SMTP credentials in .env (see DEPLOYMENT_GUIDE.md).
"""

from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig

from app.config import get_settings
from app.core.security import create_email_token

settings = get_settings()

_conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_FROM,
    MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=bool(settings.SMTP_PASSWORD),
)

_mail = FastMail(_conf)


async def send_verification_email(email: str) -> None:
    """
    Generate a verification token and send an email with the link.

    The URL format matches GET /api/v1/auth/verify/{token}.
    In production replace APP_URL with your Render domain.
    """
    token = create_email_token(email)
    verify_url = f"{settings.FRONTEND_URL}/api/v1/auth/verify/{token}"

    message = MessageSchema(
        subject="Please verify your email address",
        recipients=[email],
        body=(
            f"Hello,\n\n"
            f"Click the link below to verify your email address.\n"
            f"The link is valid for {settings.EMAIL_TOKEN_EXPIRE_HOURS} hours.\n\n"
            f"{verify_url}\n\n"
            f"If you did not register, ignore this email.\n"
        ),
        subtype=MessageType.plain,
    )

    await _mail.send_message(message)
