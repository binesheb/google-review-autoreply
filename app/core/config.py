from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Review Intelligence Platform"
    app_env: str = "development"
    app_port: int = 8000
    app_timezone: str = "UTC"

    admin_username: str = "admin"
    admin_password_hash: str = ""
    secret_key: str = ""

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "review_platform"
    postgres_user: str = "review_platform"
    postgres_password: str = ""

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "knowledge"
    ai_base_url: str = "http://localhost:11434"
    ai_model: str = "qwen3:4b"
    embedding_model: str = "embeddinggemma"

    google_enabled: bool = False
    google_access_token: str = ""
    google_account_id: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/google/oauth/callback"

    auto_publish_enabled: bool = False
    automation_paused: bool = True
    poll_interval_minutes: int = 10
    daily_publish_limit: int = 25
    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
