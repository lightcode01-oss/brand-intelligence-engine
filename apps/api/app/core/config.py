import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Configuration management settings loader powered by Pydantic Settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )
    
    # Environment profile
    ENV: Literal["development", "testing", "staging", "production"] = "development"
    
    # API specs
    API_TITLE: str = "Nomen API"
    API_DESCRIPTION: str = "AI-powered Brand Intelligence Engine API Gateway."
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Security parameters
    SECRET_KEY: str = "insecure_default_key_change_in_production_environment_secret"
    ALLOWED_HOSTS: list[str] = ["*"]
    CORS_ORIGINS: list[str] = ["*"]
    
    # Rate Limiting & Control toggles
    RATE_LIMIT_PER_MINUTE: int = 60
    MAINTENANCE_MODE: bool = False
    
    # Database URL configuration
    DATABASE_URL: str = "postgresql+asyncpg://nomen_user:secure_dev_password_change_me@localhost:5432/nomen_db"

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    @property
    def is_testing(self) -> bool:
        return self.ENV == "testing"

# Instantiate global settings object
settings = Settings()
