from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal
import re

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _read_secret_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def validate_warehouse_schema(value):
    if value is not None and (not re.fullmatch(r"[a-z][a-z0-9_]{0,62}", value)
                              or value.startswith("pg_") or value == "information_schema"):
        raise ValueError("WAREHOUSE_SCHEMA must name an application schema")
    return value


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
    warehouse_schema: str | None = Field(default=None, alias="WAREHOUSE_SCHEMA")

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
    source_intake_enabled: bool = Field(default=False, alias="SOURCE_INTAKE_ENABLED")
    source_destination: str | None = Field(default=None, alias="SOURCE_DESTINATION")
    source_service_identity: str | None = Field(default=None, alias="SOURCE_SERVICE_IDENTITY")
    source_event_mode: Literal["auto", "unverified", "classic", "longitudinal"] = Field(
        default="auto", alias="SOURCE_EVENT_MODE")

    @field_validator("warehouse_schema")
    @classmethod
    def check_warehouse_schema(cls, value):
        return validate_warehouse_schema(value)

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
