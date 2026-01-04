"""Application configuration."""

import secrets

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # CORS - Only localhost for dev, add production domains when deploying
    cors_origins: list[str] = [
        "http://localhost:8081",
        "http://localhost:19006",
        "http://localhost:3000",
    ]

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # TheMealDB (POC)
    themealdb_base_url: str = "https://www.themealdb.com/api/json/v1/1"

    # JWT Authentication - MUST be set via environment variable in production
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_expiry_minutes: int = 30
    jwt_refresh_expiry_days: int = 7

    # Rate Limiting
    rate_limit_requests: int = 5
    rate_limit_window: int = 60

    @field_validator("jwt_secret", mode="before")
    @classmethod
    def set_jwt_secret(cls, v: str) -> str:
        """Generate a secure JWT secret if not provided."""
        if not v:
            # Generate secure random secret for development
            return secrets.token_urlsafe(64)
        return v

    def validate_production_settings(self) -> None:
        """Validate that production-critical settings are properly configured."""
        if not self.debug:
            if not self.jwt_secret or self.jwt_secret == "":
                raise ValueError("JWT_SECRET must be set in production")
            if "*" in self.cors_origins:
                raise ValueError("CORS wildcard '*' is not allowed in production")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
