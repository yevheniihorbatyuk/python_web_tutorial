"""
OAuth2 Social Login Integration Example

This module demonstrates how to use OAuth2 social login (Google and GitHub)
in a FastAPI application. It shows the complete flow from obtaining an
authorization URL to exchanging the code for a user session.

OAuth2 Overview:
    OAuth2 allows users to authenticate using their existing accounts from
    providers like Google, GitHub, etc. This is more secure than storing
    passwords and provides better user experience.

    Key concepts:
    1. Authorization Code Flow: User grants app permission to access their info
    2. Token Exchange: App exchanges authorization code for access token
    3. User Info: App fetches user data using access token
    4. Session: App creates its own JWT tokens for subsequent requests

Complete Flow Example:
    1. User clicks "Login with Google" button
    2. Frontend redirects to /auth/oauth2/google/auth-url
    3. Get authorization URL pointing to Google's consent screen
    4. User authenticates and grants permission
    5. Google redirects to our callback URL with authorization code
    6. Frontend sends code to /auth/oauth2/google/callback
    7. Backend exchanges code for user info from Google
    8. Backend creates/updates user in our database
    9. Backend returns JWT tokens to frontend
    10. Frontend uses JWT tokens for subsequent API requests

Requirements:
    - Google OAuth2 credentials (from Google Cloud Console)
    - GitHub OAuth2 credentials (from GitHub Settings)
    - Set environment variables:
      * GOOGLE_CLIENT_ID
      * GOOGLE_CLIENT_SECRET
      * GOOGLE_REDIRECT_URI
      * GITHUB_CLIENT_ID
      * GITHUB_CLIENT_SECRET
      * GITHUB_REDIRECT_URI
"""

import os
from typing import Optional
from datetime import datetime
import httpx
from pydantic import BaseModel


# ============================================================================
# CONFIGURATION (from environment)
# ============================================================================

class OAuth2Config:
    """OAuth2 provider credentials and endpoints."""

    # Google OAuth2
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-client-id.apps.googleusercontent.com")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-client-secret")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/oauth2/google/callback")
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

    # GitHub OAuth2
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "your-client-id")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "your-client-secret")
    GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/auth/oauth2/github/callback")
    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USERINFO_URL = "https://api.github.com/user"
    GITHUB_EMAIL_URL = "https://api.github.com/user/emails"


# ============================================================================
# DATA MODELS
# ============================================================================

class OAuthUserInfo(BaseModel):
    """Standardized user information from any OAuth2 provider."""

    provider: str  # "google" or "github"
    provider_user_id: str  # Unique ID from provider
    email: str  # Email address
    username: str  # Username/login
    full_name: Optional[str] = None  # Display name if available
    avatar_url: Optional[str] = None  # Profile picture URL


class AuthURLRequest(BaseModel):
    """Request for OAuth2 authorization URL."""

    redirect_uri: str  # Where provider should redirect after auth


class OAuthCallbackRequest(BaseModel):
    """Request body for OAuth2 callback with authorization code."""

    code: str  # Authorization code from provider
    redirect_uri: str  # Must match the original request


# ============================================================================
# FRONTEND EXAMPLE (HTML/JavaScript)
# ============================================================================

FRONTEND_HTML_EXAMPLE = """
<!DOCTYPE html>
<html>
<head>
    <title>OAuth2 Login Example</title>
</head>
<body>
    <h1>Login with OAuth2</h1>

    <button onclick="loginWithGoogle()">Login with Google</button>
    <button onclick="loginWithGitHub()">Login with GitHub</button>

    <script>
        const API_URL = 'http://localhost:8000/auth';
        const REDIRECT_URI = window.location.origin + '/oauth2-callback';

        async function loginWithGoogle() {
            // Step 1: Get authorization URL from backend
            const response = await fetch(
                `${API_URL}/oauth2/google/auth-url?redirect_uri=${encodeURIComponent(REDIRECT_URI)}`
            );
            const data = await response.json();

            // Step 2: Redirect to Google's consent screen
            window.location.href = data.auth_url;
        }

        async function loginWithGitHub() {
            // Step 1: Get authorization URL from backend
            const response = await fetch(
                `${API_URL}/oauth2/github/auth-url?redirect_uri=${encodeURIComponent(REDIRECT_URI)}`
            );
            const data = await response.json();

            // Step 2: Redirect to GitHub's consent screen
            window.location.href = data.auth_url;
        }

        // This function is called when provider redirects back to us
        async function handleOAuth2Callback() {
            // Get authorization code from URL
            const params = new URLSearchParams(window.location.search);
            const code = params.get('code');
            const provider = params.get('provider'); // 'google' or 'github'

            if (!code) {
                alert('No authorization code received');
                return;
            }

            // Step 3: Exchange code for tokens
            const response = await fetch(
                `${API_URL}/oauth2/${provider}/callback`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        code: code,
                        redirect_uri: REDIRECT_URI
                    })
                }
            );

            const data = await response.json();

            if (response.ok) {
                // Step 4: Store JWT tokens in localStorage
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);

                // Step 5: Redirect to dashboard or home page
                window.location.href = '/dashboard';
            } else {
                alert('Authentication failed: ' + data.detail);
            }
        }
    </script>
</body>
</html>
"""


# ============================================================================
# GOOGLE OAUTH2 IMPLEMENTATION
# ============================================================================

class GoogleOAuth2:
    """Google OAuth2 integration."""

    @staticmethod
    def get_auth_url(redirect_uri: str) -> str:
        """
        Generate Google authorization URL.

        This URL should be displayed to the user for authentication.
        After user approves, Google redirects to redirect_uri with authorization code.

        Args:
            redirect_uri: Where Google should redirect after authentication

        Returns:
            Authorization URL
        """
        params = {
            'client_id': OAuth2Config.GOOGLE_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'offline',  # Allow refresh tokens
            'prompt': 'consent'  # Always show consent screen
        }

        # Build query string
        query_string = '&'.join(f'{k}={v}' for k, v in params.items())
        return f"{OAuth2Config.GOOGLE_AUTH_URL}?{query_string}"

    @staticmethod
    async def exchange_code_for_token(code: str, redirect_uri: str) -> Optional[str]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from Google
            redirect_uri: Must match the original request

        Returns:
            Access token or None if exchange failed
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    OAuth2Config.GOOGLE_TOKEN_URL,
                    data={
                        'client_id': OAuth2Config.GOOGLE_CLIENT_ID,
                        'client_secret': OAuth2Config.GOOGLE_CLIENT_SECRET,
                        'code': code,
                        'redirect_uri': redirect_uri,
                        'grant_type': 'authorization_code'
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get('access_token')
            except Exception as e:
                print(f"Token exchange failed: {e}")
                return None

    @staticmethod
    async def get_user_info(access_token: str) -> Optional[dict]:
        """
        Fetch user information from Google using access token.

        Args:
            access_token: Google access token

        Returns:
            User information dict or None if fetch failed
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    OAuth2Config.GOOGLE_USERINFO_URL,
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Failed to fetch Google user info: {e}")
                return None

    @staticmethod
    async def get_oauth_user_info(code: str, redirect_uri: str) -> Optional[OAuthUserInfo]:
        """
        Complete Google OAuth2 flow: exchange code for user information.

        Args:
            code: Authorization code from Google
            redirect_uri: Must match the original request

        Returns:
            Standardized OAuthUserInfo or None if flow failed
        """
        # Exchange code for access token
        access_token = await GoogleOAuth2.exchange_code_for_token(code, redirect_uri)
        if not access_token:
            return None

        # Fetch user information
        user_data = await GoogleOAuth2.get_user_info(access_token)
        if not user_data:
            return None

        # Standardize user info
        return OAuthUserInfo(
            provider='google',
            provider_user_id=user_data.get('sub'),
            email=user_data.get('email'),
            username=user_data.get('email', '').split('@')[0],  # Use email prefix as username
            full_name=user_data.get('name'),
            avatar_url=user_data.get('picture')
        )


# ============================================================================
# GITHUB OAUTH2 IMPLEMENTATION
# ============================================================================

class GitHubOAuth2:
    """GitHub OAuth2 integration."""

    @staticmethod
    def get_auth_url(redirect_uri: str) -> str:
        """
        Generate GitHub authorization URL.

        Args:
            redirect_uri: Where GitHub should redirect after authentication

        Returns:
            Authorization URL
        """
        params = {
            'client_id': OAuth2Config.GITHUB_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'scope': 'user:email read:user',
            'allow_signup': 'true'
        }

        query_string = '&'.join(f'{k}={v}' for k, v in params.items())
        return f"{OAuth2Config.GITHUB_AUTH_URL}?{query_string}"

    @staticmethod
    async def exchange_code_for_token(code: str, redirect_uri: str) -> Optional[str]:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from GitHub
            redirect_uri: Must match the original request

        Returns:
            Access token or None if exchange failed
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    OAuth2Config.GITHUB_TOKEN_URL,
                    data={
                        'client_id': OAuth2Config.GITHUB_CLIENT_ID,
                        'client_secret': OAuth2Config.GITHUB_CLIENT_SECRET,
                        'code': code,
                        'redirect_uri': redirect_uri
                    },
                    headers={'Accept': 'application/json'}
                )
                response.raise_for_status()
                data = response.json()
                return data.get('access_token')
            except Exception as e:
                print(f"GitHub token exchange failed: {e}")
                return None

    @staticmethod
    async def get_user_info(access_token: str) -> Optional[dict]:
        """
        Fetch user information from GitHub using access token.

        Args:
            access_token: GitHub access token

        Returns:
            User information dict or None if fetch failed
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    OAuth2Config.GITHUB_USERINFO_URL,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Accept': 'application/json'
                    }
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Failed to fetch GitHub user info: {e}")
                return None

    @staticmethod
    async def get_user_email(access_token: str) -> Optional[str]:
        """
        Fetch user's email from GitHub.

        GitHub doesn't always include email in user info, so we need
        to fetch it from a separate endpoint.

        Args:
            access_token: GitHub access token

        Returns:
            Email or None if fetch failed
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    OAuth2Config.GITHUB_EMAIL_URL,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Accept': 'application/json'
                    }
                )
                response.raise_for_status()
                emails = response.json()

                # Find primary email
                if isinstance(emails, list) and len(emails) > 0:
                    for email_data in emails:
                        if email_data.get('primary'):
                            return email_data.get('email')
                    # If no primary, return first email
                    return emails[0].get('email')
                return None
            except Exception as e:
                print(f"Failed to fetch GitHub email: {e}")
                return None

    @staticmethod
    async def get_oauth_user_info(code: str, redirect_uri: str) -> Optional[OAuthUserInfo]:
        """
        Complete GitHub OAuth2 flow: exchange code for user information.

        Args:
            code: Authorization code from GitHub
            redirect_uri: Must match the original request

        Returns:
            Standardized OAuthUserInfo or None if flow failed
        """
        # Exchange code for access token
        access_token = await GitHubOAuth2.exchange_code_for_token(code, redirect_uri)
        if not access_token:
            return None

        # Fetch user information
        user_data = await GitHubOAuth2.get_user_info(access_token)
        if not user_data:
            return None

        # Fetch email (GitHub doesn't always include it)
        email = user_data.get('email')
        if not email:
            email = await GitHubOAuth2.get_user_email(access_token)

        if not email:
            print("Warning: Could not retrieve GitHub user email")
            email = f"{user_data.get('login')}@github.local"

        # Standardize user info
        return OAuthUserInfo(
            provider='github',
            provider_user_id=str(user_data.get('id')),
            email=email,
            username=user_data.get('login'),
            full_name=user_data.get('name'),
            avatar_url=user_data.get('avatar_url')
        )


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================

async def example_google_flow():
    """
    Example: Complete Google OAuth2 flow.

    This demonstrates what happens when user authenticates with Google.
    """
    print("=== Google OAuth2 Flow ===\n")

    # Step 1: Get authorization URL (what user clicks)
    redirect_uri = "http://localhost:8000/auth/oauth2/google/callback"
    auth_url = GoogleOAuth2.get_auth_url(redirect_uri)
    print(f"1. Authorization URL (show to user):\n{auth_url}\n")

    # Step 2: User authenticates and grants permission
    # (This happens on Google's website, we don't control it)
    print("2. User authenticates at Google...")
    print("3. Google redirects with authorization code...\n")

    # Step 3: Backend receives authorization code (simulated)
    # In real flow, this comes from: code = request.query_params.get('code')
    simulated_code = "simulated-auth-code-from-google"
    print(f"4. Backend receives code: {simulated_code}\n")

    # Step 4: Exchange code for user info
    print("5. Exchanging code for Google user info...")
    user_info = await GoogleOAuth2.get_oauth_user_info(simulated_code, redirect_uri)

    if user_info:
        print(f"✓ Authentication successful!")
        print(f"  Provider: {user_info.provider}")
        print(f"  Email: {user_info.email}")
        print(f"  Username: {user_info.username}")
        print(f"  Full Name: {user_info.full_name}")
        print(f"  Avatar: {user_info.avatar_url}\n")
    else:
        print("✗ Authentication failed (code was simulated, not real)\n")


async def example_github_flow():
    """
    Example: Complete GitHub OAuth2 flow.

    This demonstrates what happens when user authenticates with GitHub.
    """
    print("=== GitHub OAuth2 Flow ===\n")

    # Step 1: Get authorization URL (what user clicks)
    redirect_uri = "http://localhost:8000/auth/oauth2/github/callback"
    auth_url = GitHubOAuth2.get_auth_url(redirect_uri)
    print(f"1. Authorization URL (show to user):\n{auth_url}\n")

    # Step 2: User authenticates and grants permission
    print("2. User authenticates at GitHub...")
    print("3. GitHub redirects with authorization code...\n")

    # Step 3: Backend receives authorization code (simulated)
    simulated_code = "simulated-auth-code-from-github"
    print(f"4. Backend receives code: {simulated_code}\n")

    # Step 4: Exchange code for user info
    print("5. Exchanging code for GitHub user info...")
    user_info = await GitHubOAuth2.get_oauth_user_info(simulated_code, redirect_uri)

    if user_info:
        print(f"✓ Authentication successful!")
        print(f"  Provider: {user_info.provider}")
        print(f"  Email: {user_info.email}")
        print(f"  Username: {user_info.username}")
        print(f"  Full Name: {user_info.full_name}")
        print(f"  Avatar: {user_info.avatar_url}\n")
    else:
        print("✗ Authentication failed (code was simulated, not real)\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import asyncio

    print("\n" + "=" * 70)
    print("OAUTH2 SOCIAL LOGIN INTEGRATION EXAMPLE")
    print("=" * 70 + "\n")

    # Run example flows
    asyncio.run(example_google_flow())
    asyncio.run(example_github_flow())

    # Print frontend example
    print("\n=== Frontend HTML/JavaScript Example ===\n")
    print(FRONTEND_HTML_EXAMPLE)

    print("\n" + "=" * 70)
    print("SETUP INSTRUCTIONS")
    print("=" * 70)
    print("""
1. GET GOOGLE CREDENTIALS:
   - Go to https://console.cloud.google.com/
   - Create a new project
   - Enable Google+ API
   - Create OAuth2 credentials (Web application)
   - Add http://localhost:8000/auth/oauth2/google/callback as redirect URI
   - Copy Client ID and Client Secret

2. GET GITHUB CREDENTIALS:
   - Go to https://github.com/settings/developers
   - Click "New OAuth App"
   - Set Authorization callback URL to http://localhost:8000/auth/oauth2/github/callback
   - Copy Client ID and Client Secret

3. SET ENVIRONMENT VARIABLES:
   export GOOGLE_CLIENT_ID="your-google-client-id"
   export GOOGLE_CLIENT_SECRET="your-google-client-secret"
   export GITHUB_CLIENT_ID="your-github-client-id"
   export GITHUB_CLIENT_SECRET="your-github-client-secret"

4. UPDATE REDIRECT URIs:
   - If not using localhost, update GOOGLE_REDIRECT_URI and GITHUB_REDIRECT_URI
   - Must match URLs in provider settings

5. RUN YOUR FASTAPI APP:
   uvicorn app.main:app --reload

6. TEST IN BROWSER:
   - Visit http://localhost:8000/docs (Swagger UI)
   - Test endpoints:
     * GET /auth/oauth2/google/auth-url?redirect_uri=...
     * GET /auth/oauth2/github/auth-url?redirect_uri=...
     * POST /auth/oauth2/google/callback
     * POST /auth/oauth2/github/callback
    """)
