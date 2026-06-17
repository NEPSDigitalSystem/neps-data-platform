from __future__ import annotations

import etl.sync.orchestrator as orchestrator_module
from etl.models.metadata import MetadataModel
from etl.transform.mock_schema import get_backend_instruments


class _BeginContext:
    def __enter__(self):
        return object()

    def __exit__(self, exc_type, exc, traceback):
        return False


class FakeEngine:
    def begin(self):
        return _BeginContext()


class FakeRunLogger:
    run_id = "run-1"

    def start(self, **kwargs):
        self.started = kwargs

    def finish(self, **kwargs):
        self.finished = kwargs


class FakeStateStore:
    def __init__(self, engine):
        self.updated = None

    def get_watermark(self, *, project_id: str, entity_name: str) -> str:
        return "2025-03-01T00:00:00+00:00"

    def update_state(self, **kwargs):
        self.updated = kwargs


class FakeClient:
    source_mode = "mock"

    def __init__(self):
        self.date_range_begin = None

    def export_metadata(self):
        return MetadataModel(
            project_id="NEPS-2025",
            project_title="NEPS Digital",
            instruments=get_backend_instruments(),
            events=[],
            raw={},
            source_mode="mock",
        )

    def export_records(self, *, date_range_begin=None, fields=None, events=None):
        self.date_range_begin = date_range_begin
        return []


def _patch_orchestrator(monkeypatch, client: FakeClient) -> None:
    monkeypatch.setattr(orchestrator_module, "create_db_engine", lambda settings: FakeEngine())
    monkeypatch.setattr(orchestrator_module, "get_redcap_client", lambda settings: client)
    monkeypatch.setattr(orchestrator_module, "RunLogger", lambda engine: FakeRunLogger())
    monkeypatch.setattr(orchestrator_module, "SyncStateStore", lambda engine: FakeStateStore(engine))
    monkeypatch.setattr(orchestrator_module, "persist_metadata", lambda *args, **kwargs: None)
    monkeypatch.setattr(orchestrator_module, "load_instrument_records", lambda *args, **kwargs: 0)
    monkeypatch.setattr(orchestrator_module, "refresh_views", lambda *args, **kwargs: None)


def test_mock_sync_uses_incremental_watermark_by_default(monkeypatch, mock_settings) -> None:
    client = FakeClient()
    _patch_orchestrator(monkeypatch, client)

    orchestrator = orchestrator_module.SyncOrchestrator(mock_settings)
    result = orchestrator.sync()

    assert result["sync_type"] == "incremental"
    assert client.date_range_begin == "2025-03-01T00:00:00+00:00"


def test_full_sync_does_not_pass_watermark(monkeypatch, mock_settings) -> None:
    client = FakeClient()
    _patch_orchestrator(monkeypatch, client)

    orchestrator = orchestrator_module.SyncOrchestrator(mock_settings)
    result = orchestrator.sync(full=True)

    assert result["sync_type"] == "full"
    assert client.date_range_begin is None
