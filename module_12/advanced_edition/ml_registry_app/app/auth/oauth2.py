"""OAuth2 social login integration (Google, GitHub, etc.)"""

from typing import Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import httpx
import os

from ..models.user import User


class OAuthProvider(str):
    """Supported OAuth2 providers"""
    GOOGLE = "google"
    GITHUB = "github"


class OAuthConfig:
    """OAuth2 configuration for different providers"""

    @staticmethod
    def get_config(provider: str) -> Dict[str, str]:
        """Get OAuth2 configuration for a provider"""
        configs = {
            OAuthProvider.GOOGLE: {
                "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://openidconnect.googleapis.com/v1/userinfo",
                "scopes": ["openid", "email", "profile"],
            },
            OAuthProvider.GITHUB: {
                "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
                "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
                "auth_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
                "scopes": ["user:email", "read:user"],
            },
        }
        return configs.get(provider, {})


class OAuthUserInfo(BaseModel):
    """User information from OAuth2 provider"""
    provider: str
    provider_user_id: str
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


async def exchange_code_for_token(
    provider: str,
    code: str,
    redirect_uri: str,
) -> Optional[str]:
    """
    Exchange OAuth2 authorization code for access token.

    Args:
        provider: OAuth2 provider (google, github)
        code: Authorization code from OAuth2 provider
        redirect_uri: Redirect URI used in authorization request

    Returns:
        Access token or None if exchange fails
    """
    config = OAuthConfig.get_config(provider)
    if not config.get("client_id"):
        return None

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                config["token_url"],
                data={
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("access_token")
        except Exception as e:
            print(f"Token exchange error: {e}")
            return None


async def get_user_info_from_provider(
    provider: str,
    access_token: str,
) -> Optional[Dict[str, Any]]:
    """
    Get user information from OAuth2 provider using access token.

    Args:
        provider: OAuth2 provider (google, github)
        access_token: OAuth2 access token

    Returns:
        User info dict or None if request fails
    """
    config = OAuthConfig.get_config(provider)
    userinfo_url = config.get("userinfo_url")

    if not userinfo_url:
        return None

    async with httpx.AsyncClient() as client:
        try:
            if provider == OAuthProvider.GITHUB:
                # GitHub needs Accept header
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                }
            else:
                # Google uses Authorization header
                headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.get(userinfo_url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"User info request error: {e}")
            return None


def parse_oauth_user_info(provider: str, provider_data: Dict[str, Any]) -> Optional[OAuthUserInfo]:
    """
    Parse user information from OAuth2 provider into standard format.

    Args:
        provider: OAuth2 provider
        provider_data: Raw user data from provider

    Returns:
        Standardized user info
    """
    try:
        if provider == OAuthProvider.GOOGLE:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=provider_data.get("sub"),
                email=provider_data.get("email"),
                username=provider_data.get("email", "").split("@")[0],
                full_name=provider_data.get("name"),
                avatar_url=provider_data.get("picture"),
            )
        elif provider == OAuthProvider.GITHUB:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=str(provider_data.get("id")),
                email=provider_data.get("email"),
                username=provider_data.get("login"),
                full_name=provider_data.get("name"),
                avatar_url=provider_data.get("avatar_url"),
            )
    except Exception as e:
        print(f"Parse error for {provider}: {e}")
        return None

    return None


async def get_or_create_oauth_user(
    db: AsyncSession,
    oauth_user_info: OAuthUserInfo,
) -> Optional[User]:
    """
    Get existing user by OAuth credentials or create new one.

    Args:
        db: Database session
        oauth_user_info: User info from OAuth2 provider

    Returns:
        User object or None if creation fails
    """
    # Try to find user by email
    result = await db.execute(
        select(User).where(User.email == oauth_user_info.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        # Update user info from OAuth provider
        existing_user.full_name = oauth_user_info.full_name
        existing_user.is_active = True
        existing_user.updated_at = datetime.utcnow()
        await db.commit()
        return existing_user

    # Create new user from OAuth info
    try:
        new_user = User(
            email=oauth_user_info.email,
            username=oauth_user_info.username,
            full_name=oauth_user_info.full_name,
            hashed_password="oauth-" + oauth_user_info.provider,  # Marker for OAuth users
            is_active=True,
            role="user",  # Default role for OAuth users
        )
        db.add(new_user)
        await db.flush()  # Get the new user's ID

        # In a real app, you'd store the OAuth account link here
        # For now, we just return the user
        await db.commit()
        return new_user
    except Exception as e:
        print(f"User creation error: {e}")
        await db.rollback()
        return None


class GoogleOAuth2:
    """Google OAuth2 implementation"""

    @staticmethod
    def get_auth_url(redirect_uri: str, state: str) -> str:
        """Generate Google OAuth2 authorization URL"""
        config = OAuthConfig.get_config(OAuthProvider.GOOGLE)
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(config["scopes"]),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config['auth_url']}?{param_str}"

    @staticmethod
    async def handle_callback(
        code: str,
        redirect_uri: str,
        db: AsyncSession,
    ) -> Optional[User]:
        """
        Handle Google OAuth2 callback.

        Args:
            code: Authorization code from Google
            redirect_uri: Redirect URI
            db: Database session

        Returns:
            User object or None
        """
        # Exchange code for token
        token = await exchange_code_for_token(
            OAuthProvider.GOOGLE,
            code,
            redirect_uri,
        )
        if not token:
            return None

        # Get user info
        user_data = await get_user_info_from_provider(OAuthProvider.GOOGLE, token)
        if not user_data:
            return None

        # Parse and create user
        oauth_user = parse_oauth_user_info(OAuthProvider.GOOGLE, user_data)
        if not oauth_user:
            return None

        return await get_or_create_oauth_user(db, oauth_user)


class GitHubOAuth2:
    """GitHub OAuth2 implementation"""

    @staticmethod
    def get_auth_url(redirect_uri: str, state: str) -> str:
        """Generate GitHub OAuth2 authorization URL"""
        config = OAuthConfig.get_config(OAuthProvider.GITHUB)
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": ",".join(config["scopes"]),
            "state": state,
            "allow_signup": "true",
        }
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config['auth_url']}?{param_str}"

    @staticmethod
    async def handle_callback(
        code: str,
        redirect_uri: str,
        db: AsyncSession,
    ) -> Optional[User]:
        """
        Handle GitHub OAuth2 callback.

        Args:
            code: Authorization code from GitHub
            redirect_uri: Redirect URI
            db: Database session

        Returns:
            User object or None
        """
        # Exchange code for token
        token = await exchange_code_for_token(
            OAuthProvider.GITHUB,
            code,
            redirect_uri,
        )
        if not token:
            return None

        # Get user info
        user_data = await get_user_info_from_provider(OAuthProvider.GITHUB, token)
        if not user_data:
            return None

        # Get email if not in main response (GitHub often doesn't return email)
        if not user_data.get("email"):
            async with httpx.AsyncClient() as client:
                try:
                    email_response = await client.get(
                        "https://api.github.com/user/emails",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Accept": "application/vnd.github.v3+json",
                        },
                    )
                    email_data = email_response.json()
                    if email_data:
                        user_data["email"] = email_data[0].get("email")
                except Exception:
                    pass

        # Parse and create user
        oauth_user = parse_oauth_user_info(OAuthProvider.GITHUB, user_data)
        if not oauth_user:
            return None

        return await get_or_create_oauth_user(db, oauth_user)
