from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://reviewai:reviewai@localhost:5432/reviewai"
    qdrant_url: str = "http://localhost:6333"
    ai_base_url: str = "http://localhost:11434"
    ai_model: str = "qwen3:4b"
    ai_api_key: str = ""
    google_enabled: bool = False
    google_account_id: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/google/oauth/callback"
    auto_publish_enabled: bool = False
    poll_interval_minutes: int = 10
    daily_publish_limit: int = 25
    log_level: str = "INFO"
    secret_key: str = "change-me-in-production"

settings = Settings()
