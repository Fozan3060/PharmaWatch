from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Gemini
    gemini_api_key: str = ""
    gemini_agent_model: str = "gemini-2.5-flash"
    gemini_synthesis_model: str = "gemini-2.5-pro"

    # Firebase
    firebase_credentials_path: str = "./firebase-credentials.json"
    firebase_project_id: str = ""

    # Google Maps
    google_maps_api_key: str = ""

    # Local data
    drap_sqlite_path: str = "./data_store/drap.sqlite"

    # Server
    app_env: str = "dev"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Agent
    agent_max_tool_calls: int = 15
    agent_timeout_seconds: int = 30

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def drap_sqlite_abspath(self) -> Path:
        return Path(self.drap_sqlite_path).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
