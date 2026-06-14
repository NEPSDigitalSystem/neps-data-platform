from __future__ import annotations

from pathlib import Path


def test_dockerignore_excludes_mock_redcap_service() -> None:
    dockerignore = Path(".dockerignore").read_text(encoding="utf-8")
    assert "mock-redcap-service/" in dockerignore
    assert "tests/" in dockerignore
