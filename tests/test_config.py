from __future__ import annotations

from pathlib import Path

from etl.config import Settings


def test_settings_defaults(mock_settings: Settings) -> None:
    assert mock_settings.redcap_mock_enabled is True
    assert mock_settings.source_mode == "mock"


def test_production_requires_token() -> None:
    try:
        Settings(
            DATABASE_URL="postgresql://neps:neps_password@localhost:5432/neps_db",
            REDCAP_API_URL="https://kcird.org/api/",
            REDCAP_MOCK_ENABLED=False,
        )
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_settings_from_token_file(tmp_path: Path) -> None:
    token_file = tmp_path / "redcap_token"
    token_file.write_text("abc123", encoding="utf-8")

    settings = Settings(
        DATABASE_URL="postgresql://neps:neps_password@localhost:5432/neps_db",
        REDCAP_API_URL="https://kcird.org/api/",
        REDCAP_API_TOKEN_FILE=str(token_file),
        REDCAP_MOCK_ENABLED=False,
    )
    assert settings.redcap_api_token == "abc123"
