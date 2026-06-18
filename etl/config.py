from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _read_secret_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_env: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    database_url: str = Field(
        default="postgresql://neps:neps_password@localhost:5432/neps_db",
        alias="DATABASE_URL",
    )
    database_url_file: str | None = Field(default=None, alias="DATABASE_URL_FILE")

    redcap_api_url: str = Field(
        default="http://localhost:8000/api/redcap",
        alias="REDCAP_API_URL",
    )
    redcap_api_token: str | None = Field(default=None, alias="REDCAP_API_TOKEN")
    redcap_api_token_file: str | None = Field(default=None, alias="REDCAP_API_TOKEN_FILE")
    redcap_mock_enabled: bool = Field(default=True, alias="REDCAP_MOCK_ENABLED")
    redcap_project_id: str = Field(default="NEPS-2025", alias="REDCAP_PROJECT_ID")

    http_timeout_seconds: int = 120
    http_max_retries: int = 3

    @model_validator(mode="after")
    def resolve_secrets(self) -> Settings:
        if self.database_url_file:
            object.__setattr__(self, "database_url", _read_secret_file(self.database_url_file))

        if self.redcap_api_token_file:
            object.__setattr__(
                self,
                "redcap_api_token",
                _read_secret_file(self.redcap_api_token_file),
            )

        if not self.redcap_mock_enabled and not self.redcap_api_token:
            raise ValueError(
                "REDCAP_API_TOKEN or REDCAP_API_TOKEN_FILE is required when REDCAP_MOCK_ENABLED=false"
            )

        return self

    @property
    def source_mode(self) -> Literal["mock", "production"]:
        return "mock" if self.redcap_mock_enabled else "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
