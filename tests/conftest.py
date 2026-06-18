from __future__ import annotations

import json
from pathlib import Path

import pytest

from etl.config import Settings


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_metadata(fixtures_dir: Path) -> dict:
    return json.loads((fixtures_dir / "mock_metadata.json").read_text(encoding="utf-8"))


@pytest.fixture
def mock_records(fixtures_dir: Path) -> list[dict]:
    return json.loads((fixtures_dir / "mock_records.json").read_text(encoding="utf-8"))


@pytest.fixture
def mock_settings() -> Settings:
    return Settings(
        DATABASE_URL="postgresql://neps:neps_password@localhost:5432/neps_db",
        REDCAP_API_URL="http://mock-redcap.test/api/redcap",
        REDCAP_API_TOKEN="mock_token_for_development_only",
        REDCAP_MOCK_ENABLED=True,
        REDCAP_PROJECT_ID="NEPS-2025",
    )
