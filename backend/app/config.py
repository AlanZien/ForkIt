"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: list[str] = ["http://localhost:8081", "http://localhost:19006"]

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # TheMealDB (POC)
    themealdb_base_url: str = "https://www.themealdb.com/api/json/v1/1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
