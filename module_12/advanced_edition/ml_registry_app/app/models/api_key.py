"""
API Key model for service-to-service authentication.

API keys allow external services to authenticate with our API without
requiring user interaction. They're useful for:
- Automated systems (CI/CD pipelines, scheduled jobs)
- Third-party integrations
- Backend-to-backend service communication
- Scripts and command-line tools

Security considerations:
- API keys should be treated like passwords
- Always use HTTPS when transmitting API keys
- Rotate keys periodically
- Use rate limiting to prevent abuse
- Log all API key usage for audit trails
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class APIKey(Base):
    """API Key for service-to-service authentication."""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Key metadata
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # The actual key (hashed version, never stored in plain)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Ownership and scope
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="api_keys")

    # Permissions and scopes (stored as comma-separated string)
    # Examples: "read:models,write:models", "read:*"
    scopes: Mapped[str] = mapped_column(String(500), default="read:*")

    # Status and expiration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    # Rate limiting
    rate_limit_requests: Mapped[int] = mapped_column(default=1000)  # per hour
    rate_limit_window_seconds: Mapped[int] = mapped_column(default=3600)  # 1 hour

    # Usage tracking
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_requests: Mapped[int] = mapped_column(default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name='{self.name}', user_id={self.user_id})>"

    def is_expired(self) -> bool:
        """Check if API key is expired."""
        if self.expires_at is None:
            return False
        return datetime.now(self.expires_at.tzinfo) > self.expires_at

    def is_valid(self) -> bool:
        """Check if API key is valid (active and not expired)."""
        return self.is_active and not self.is_expired()

    def has_scope(self, required_scope: str) -> bool:
        """
        Check if API key has required scope.

        Scope format: "resource:action" (e.g., "models:read", "experiments:write")
        Wildcard "*" grants all scopes for resource or globally.

        Examples:
            - Key has scope "read:*" → has_scope("models:read") → True
            - Key has scope "models:*" → has_scope("models:write") → True
            - Key has scope "models:read" → has_scope("models:read") → True
            - Key has scope "models:read" → has_scope("models:write") → False
            - Key has scope "*:*" or "*" → has_scope(anything) → True
        """
        # Superscope: has all permissions
        if "*:*" in self.scopes or "*" in self.scopes:
            return True

        scopes_list = [s.strip() for s in self.scopes.split(",")]

        for scope in scopes_list:
            if scope == required_scope:
                # Exact match
                return True

            # Wildcard matching
            if ":" in scope:
                resource, action = scope.split(":", 1)
                required_resource, required_action = required_scope.split(":", 1)

                # resource:* matches any action on that resource
                if resource == required_resource and action == "*":
                    return True

                # *:action matches any resource with that action
                if resource == "*" and action == required_action:
                    return True

        return False
