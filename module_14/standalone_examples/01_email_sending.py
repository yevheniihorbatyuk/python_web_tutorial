"""
01. Email Sending: smtplib → aiosmtplib → FastAPI-Mail
=======================================================

Three approaches to sending email in Python. The progression shows
why blocking I/O matters in async web applications.

Requirements for running:
    Start MailHog: docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog
    pip install fastapi fastapi-mail uvicorn

After running each section, check http://localhost:8025 to see received emails.
"""

# ============================================================
# SECTION 1: smtplib — Synchronous (standard library)
# ============================================================
"""
smtplib is built into Python and works fine for scripts and CLI tools.
The problem: it is BLOCKING. In an async FastAPI endpoint, calling
a blocking function pauses the entire event loop — no other requests
can be processed while your email is sending.

Use smtplib:  ✅ Scripts, CLI tools, cron jobs
Avoid in:     ❌ FastAPI/asyncio applications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email_smtplib(to: str, subject: str, body: str) -> None:
    """Send email using smtplib (synchronous)."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "sender@example.com"
    msg["To"] = to

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("localhost", 1025) as server:
        # MailHog doesn't require auth — real SMTP does:
        # server.starttls()
        # server.login(username, password)
        server.sendmail("sender@example.com", to, msg.as_string())


# Demonstrate the blocking problem:
import asyncio
import time


async def demonstrate_blocking_problem():
    """Show that smtplib blocks the event loop."""
    print("=== Demonstrating blocking I/O problem ===")

    start = time.time()

    async def background_task():
        """This task should run concurrently."""
        await asyncio.sleep(0.1)
        print(f"  Background task ran at {time.time() - start:.2f}s")

    # With a blocking call, background task is delayed:
    print("Starting background task...")
    task = asyncio.create_task(background_task())

    # Simulate a blocking SMTP call (0.5s sleep stands in for real SMTP)
    print("Simulating blocking SMTP call (0.5s)...")
    time.sleep(0.5)  # This blocks the event loop!

    await task
    print(f"Total time: {time.time() - start:.2f}s")
    print("  → Background task was delayed by blocking SMTP call\n")


# ============================================================
# SECTION 2: aiosmtplib — Async SMTP (drop-in replacement)
# ============================================================
"""
aiosmtplib wraps the smtplib interface with async/await.
No event loop blocking. Runs the SMTP connection as a coroutine.

Install: pip install aiosmtplib
"""

try:
    import aiosmtplib

    async def send_email_async(to: str, subject: str, body: str) -> None:
        """Send email using aiosmtplib (async, non-blocking)."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = "sender@example.com"
        msg["To"] = to
        msg.attach(MIMEText(body, "plain"))

        await aiosmtplib.send(
            msg,
            hostname="localhost",
            port=1025,
            # For Gmail:
            # hostname="smtp.gmail.com",
            # port=587,
            # username="your@gmail.com",
            # password="app-password",
            # start_tls=True,
        )

    async def demonstrate_nonblocking():
        """Show that aiosmtplib doesn't block the event loop."""
        print("=== Demonstrating non-blocking async SMTP ===")
        start = time.time()

        async def background_task():
            await asyncio.sleep(0.1)
            print(f"  Background task ran at {time.time() - start:.2f}s")

        task = asyncio.create_task(background_task())
        print("Sending email asynchronously...")
        # Background task can run while email sends:
        await send_email_async("test@example.com", "Async Test", "Hello from aiosmtplib")
        await task
        print(f"  Email sent. Background task ran concurrently.\n")

except ImportError:
    print("aiosmtplib not installed. Run: pip install aiosmtplib\n")


# ============================================================
# SECTION 3: FastAPI-Mail — Production pattern
# ============================================================
"""
FastAPI-Mail builds on aiosmtplib and adds:
- Jinja2 HTML email templates
- Pydantic configuration (integrates with Settings)
- Background sending (optional)
- Simple API that matches FastAPI's style

This is the approach used in contacts_api.
"""

from fastapi import FastAPI, BackgroundTasks
from pydantic import EmailStr

try:
    from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

    # Configuration (in production, comes from Settings via pydantic-settings)
    mail_conf = ConnectionConfig(
        MAIL_USERNAME="test@example.com",
        MAIL_PASSWORD="",
        MAIL_FROM="test@example.com",
        MAIL_PORT=1025,
        MAIL_SERVER="localhost",
        MAIL_FROM_NAME="Contacts App",
        MAIL_STARTTLS=False,   # MailHog doesn't use TLS
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=False,
        VALIDATE_CERTS=False,
    )

    fast_mail = FastMail(mail_conf)

    async def send_verification_email_example(to_email: str, verification_url: str):
        """Send a verification email using FastAPI-Mail."""
        message = MessageSchema(
            subject="Verify your email",
            recipients=[to_email],
            body=f"""
            <h2>Welcome to Contacts App!</h2>
            <p>Click the link below to verify your email:</p>
            <a href="{verification_url}">Verify Email</a>
            <p>This link expires in 24 hours.</p>
            """,
            subtype=MessageType.html,
        )
        await fast_mail.send_message(message)
        print(f"  Verification email sent to {to_email}")

    # Minimal FastAPI app to demonstrate
    app = FastAPI(title="Email Demo")

    @app.post("/send-verification")
    async def demo_send_email(email: str = "demo@example.com"):
        url = "http://localhost:8000/verify?token=example-token"
        await send_verification_email_example(email, url)
        return {"message": f"Verification email sent to {email}. Check http://localhost:8025"}

except ImportError:
    print("fastapi-mail not installed. Run: pip install fastapi-mail\n")
    app = FastAPI()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("Email Sending Approaches Demo")
    print("=" * 50)
    print()
    print("Prerequisites:")
    print("  docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog")
    print("  Check emails at: http://localhost:8025")
    print()

    async def main():
        # Section 1: Show blocking problem (simulation only, no MailHog needed)
        await demonstrate_blocking_problem()

        # Section 2: aiosmtplib (requires MailHog)
        try:
            await demonstrate_nonblocking()
        except Exception as e:
            print(f"aiosmtplib demo skipped (MailHog not running?): {e}\n")

        # Section 3: FastAPI-Mail via uvicorn
        print("=== FastAPI-Mail Demo ===")
        print("Run the FastAPI app:")
        print("  uvicorn 01_email_sending:app --reload")
        print("Then POST to:")
        print("  http://localhost:8000/send-verification")
        print("Check emails at:")
        print("  http://localhost:8025")

    asyncio.run(main())
