"""SSO provider abstraction layer: base contract and provider implementations."""
import uuid
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.security import SSOProvider, SecurityPolicy


class BaseSSO(ABC):
    """Abstract base for all OAuth2/OIDC SSO providers."""

    provider_name: str = ""

    @abstractmethod
    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """Return the provider's OAuth2 authorization endpoint URL."""
        ...

    @abstractmethod
    async def exchange_code(self, code: str, redirect_uri: str) -> dict:
        """Exchange the authorization code for tokens and user profile."""
        ...

    @abstractmethod
    def get_scopes(self) -> list[str]:
        """Return required OAuth2 scopes."""
        ...


class GoogleSSO(BaseSSO):
    """Google OAuth2 / OpenID Connect SSO provider."""

    provider_name = "google"
    _AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    _TOKEN_URL = "https://oauth2.googleapis.com/token"
    _USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret

    def get_scopes(self) -> list[str]:
        return ["openid", "email", "profile"]

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        scopes = "%20".join(self.get_scopes())
        return (
            f"{self._AUTH_URL}?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
            f"&access_type=offline&prompt=select_account"
        )

    async def exchange_code(self, code: str, redirect_uri: str) -> dict:
        """In production: perform actual HTTP exchange with Google token endpoint."""
        # Stub — real implementation would use httpx to POST to _TOKEN_URL then GET _USERINFO_URL
        return {
            "provider": "google",
            "email": "user@example.com",
            "name": "Example User",
            "sub": "google_sub_id_placeholder",
            "picture": None,
        }


class MicrosoftSSO(BaseSSO):
    """Microsoft Azure AD / Entra ID OAuth2 / OpenID Connect provider."""

    provider_name = "microsoft"
    _AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    _TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

    def __init__(self, client_id: str, client_secret: str, tenant_id: str = "common") -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

    def get_scopes(self) -> list[str]:
        return ["openid", "email", "profile", "offline_access"]

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        scopes = "%20".join(self.get_scopes())
        auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        return (
            f"{auth_url}?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
        )

    async def exchange_code(self, code: str, redirect_uri: str) -> dict:
        return {
            "provider": "microsoft",
            "email": "user@company.com",
            "name": "Example User",
            "sub": "ms_sub_id_placeholder",
            "picture": None,
        }


class OktaSSO(BaseSSO):
    """Okta OpenID Connect enterprise SSO provider."""

    provider_name = "okta"

    def __init__(self, client_id: str, client_secret: str, domain: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.domain = domain  # e.g. "company.okta.com"

    def get_scopes(self) -> list[str]:
        return ["openid", "email", "profile", "groups"]

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        scopes = "%20".join(self.get_scopes())
        return (
            f"https://{self.domain}/oauth2/v1/authorize?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scopes}"
            f"&state={state}"
        )

    async def exchange_code(self, code: str, redirect_uri: str) -> dict:
        return {
            "provider": "okta",
            "email": "user@enterprise.com",
            "name": "Enterprise User",
            "sub": "okta_sub_id_placeholder",
            "groups": [],
        }


# Provider registry
_PROVIDER_MAP = {
    "google": GoogleSSO,
    "microsoft": MicrosoftSSO,
    "okta": OktaSSO,
}


class SSOService:
    """Orchestrates SSO provider configuration and workspace authentication flows."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_provider(self, workspace_id: uuid.UUID) -> Optional[BaseSSO]:
        """Retrieve the configured SSO provider for a workspace."""
        result = await self.db.execute(
            select(SSOProvider).where(
                SSOProvider.workspace_id == workspace_id,
                SSOProvider.is_active == True,
            )
        )
        config = result.scalar_one_or_none()
        if not config:
            return None

        cls = _PROVIDER_MAP.get(config.provider)
        if not cls:
            return None

        if config.provider == "okta":
            domain = config.metadata_json.get("domain", "")
            return cls(config.client_id, config.client_secret_encrypted, domain)
        return cls(config.client_id, config.client_secret_encrypted)

    async def configure_sso(
        self,
        workspace_id: uuid.UUID,
        provider: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        metadata: Optional[dict] = None,
    ) -> dict:
        """Create or update SSO provider configuration for a workspace."""
        if provider not in _PROVIDER_MAP:
            return {"success": False, "error": f"Unsupported SSO provider: {provider}"}

        result = await self.db.execute(
            select(SSOProvider).where(SSOProvider.workspace_id == workspace_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.provider = provider
            existing.client_id = client_id
            existing.client_secret_encrypted = client_secret  # encrypt in production
            existing.redirect_uri = redirect_uri
            existing.metadata_json = metadata or {}
            existing.is_active = True
        else:
            config = SSOProvider(
                workspace_id=workspace_id,
                provider=provider,
                client_id=client_id,
                client_secret_encrypted=client_secret,
                redirect_uri=redirect_uri,
                metadata_json=metadata or {},
                is_active=True,
            )
            self.db.add(config)

        await self.db.flush()
        return {"success": True, "provider": provider}

    async def get_sso_config(self, workspace_id: uuid.UUID) -> Optional[dict]:
        """Return the current SSO configuration for a workspace (sans secrets)."""
        result = await self.db.execute(
            select(SSOProvider).where(SSOProvider.workspace_id == workspace_id)
        )
        config = result.scalar_one_or_none()
        if not config:
            return None
        return {
            "id": str(config.id),
            "provider": config.provider,
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "is_active": config.is_active,
            "metadata": config.metadata_json,
        }

    def get_available_providers(self) -> list[str]:
        return list(_PROVIDER_MAP.keys())
