from typing import Optional

def get_google_auth_url() -> str:
    """Generates the OAuth redirect URL for Google accounts authorization."""
    return "https://accounts.google.com/o/oauth2/v2/auth?client_id=google_client_id&response_type=code&scope=openid%20email%20profile&redirect_uri=https://nomen.ai/api/v1/auth/google/callback"

def get_github_auth_url() -> str:
    """Generates the OAuth redirect URL for GitHub accounts authorization."""
    return "https://github.com/login/oauth/authorize?client_id=github_client_id&scope=user:email&redirect_uri=https://nomen.ai/api/v1/auth/github/callback"

async def verify_google_oauth_callback(code: str) -> dict[str, str]:
    """Exchanges a Google authorization code for verified user email profile details."""
    # Placeholder exchange flow. Returns profile mapping.
    if code == "invalid_google_code":
        raise ValueError("Invalid Google OAuth authorization code.")
    return {
        "email": "oauth.google@nomen.ai",
        "name": "Google User",
        "avatar": "https://lh3.googleusercontent.com/avatar"
    }

async def verify_github_oauth_callback(code: str) -> dict[str, str]:
    """Exchanges a GitHub authorization code for verified user email profile details."""
    # Placeholder exchange flow.
    if code == "invalid_github_code":
        raise ValueError("Invalid GitHub OAuth authorization code.")
    return {
        "email": "oauth.github@nomen.ai",
        "name": "GitHub User",
        "avatar": "https://avatars.githubusercontent.com/avatar"
    }
