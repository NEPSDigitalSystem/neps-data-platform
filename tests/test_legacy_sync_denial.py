import pytest
from etl.sync.orchestrator import SyncOrchestrator


def test_legacy_sync_denies_before_accessing_transport_or_database():
    # Uninitialised object has no engine/client/state; denial must precede them.
    source = object.__new__(SyncOrchestrator)
    with pytest.raises(PermissionError, match='Legacy sync disabled'):
        source.sync(full=True)
    with pytest.raises(PermissionError, match='Legacy sync disabled'):
        source.sync(metadata_only=True, dry_run=True)
