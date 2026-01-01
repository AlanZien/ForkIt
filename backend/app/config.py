"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: list[str] = [
        "http://localhost:8081",
        "http://localhost:19006",
        "http://192.168.1.27:8081",
        "http://192.168.1.27:19006",
        "exp://192.168.1.27:8081",
        "*",  # Allow all for development
    ]

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # TheMealDB (POC)
    themealdb_base_url: str = "https://www.themealdb.com/api/json/v1/1"

    # JWT Authentication
    jwt_secret: str = "your-super-secret-key-min-32-chars-here"
    jwt_algorithm: str = "HS256"
    jwt_access_expiry_minutes: int = 30
    jwt_refresh_expiry_days: int = 7

    # Rate Limiting
    rate_limit_requests: int = 5
    rate_limit_window: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
