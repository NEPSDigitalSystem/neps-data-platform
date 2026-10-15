"""Integration boundaries, using synthetic settings and no external services."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from etl import main
from etl.analytics.distress_trends import analyze_distress_trends
from etl.config import Settings
from etl.sync import orchestrator


@pytest.mark.parametrize("options", [
    {}, {"full": True}, {"metadata_only": True}, {"dry_run": True},
    {"metadata_only": True, "dry_run": True},
])
def test_retired_sync_never_constructs_transport_or_engine(monkeypatch, options):
    engine = Mock(side_effect=AssertionError("Database construction forbidden"))
    client = Mock(side_effect=AssertionError("Transport construction forbidden"))
    monkeypatch.setattr(orchestrator, "create_db_engine", engine)
    monkeypatch.setattr(orchestrator, "get_redcap_client", client)
    instance = orchestrator.SyncOrchestrator(Settings(_env_file=None))
    with pytest.raises(PermissionError, match="Legacy sync disabled"):
        instance.sync(**options)
    engine.assert_not_called()
    client.assert_not_called()


@pytest.mark.parametrize("argv", [
    ["sync"], ["sync", "--full"], ["sync", "--metadata-only"],
    ["sync", "--dry-run"],
])
def test_retired_sync_cli_fails_without_orchestrator_or_collector(monkeypatch, capsys, argv):
    settings = SimpleNamespace(source_intake_enabled=False)
    monkeypatch.setattr(main, "get_settings", lambda: settings)
    forbidden = Mock(side_effect=AssertionError("Retired sync must not run"))
    monkeypatch.setattr(main, "SyncOrchestrator", forbidden)
    monkeypatch.setattr(main, "cmd_collect_source", forbidden)
    args = main.build_parser().parse_args(argv)
    assert args.func(args) == 1
    forbidden.assert_not_called()
    assert "legacy_sync_disabled" in capsys.readouterr().out


def test_retired_analysis_library_and_cli_fail_without_configuration(monkeypatch, capsys):
    forbidden = Mock(side_effect=AssertionError("No settings or secrets needed"))
    monkeypatch.setattr(main, "get_settings", forbidden)
    with pytest.raises(PermissionError, match="Legacy distress analysis disabled"):
        analyze_distress_trends()
    args = main.build_parser().parse_args(["analyze"])
    assert args.func(args) == 1
    forbidden.assert_not_called()
    assert "legacy_analysis_disabled" in capsys.readouterr().out


def test_enabled_sync_dispatches_only_to_independent_collector(monkeypatch):
    monkeypatch.setattr(main, "get_settings", lambda: SimpleNamespace(source_intake_enabled=True))
    collect = Mock(return_value=0)
    monkeypatch.setattr(main, "cmd_collect_source", collect)
    args = main.build_parser().parse_args(["sync", "--full"])
    assert args.func(args) == 0
    collect.assert_called_once_with(args)


@pytest.mark.parametrize("option", ["--metadata-only", "--dry-run"])
def test_source_alias_rejects_legacy_options_before_collection(monkeypatch, option):
    monkeypatch.setattr(main, "get_settings", lambda: SimpleNamespace(source_intake_enabled=True))
    collect = Mock(side_effect=AssertionError("No source collection expected"))
    monkeypatch.setattr(main, "cmd_collect_source", collect)
    args = main.build_parser().parse_args(["sync", option])
    assert args.func(args) == 1
    collect.assert_not_called()


@pytest.mark.parametrize("command", ["sync", "collect-source"])
def test_configuration_failure_exits_nonzero_without_sensitive_error(monkeypatch, capsys, command):
    marker = "SYNTHETIC-SENSITIVE-CONFIGURATION"
    monkeypatch.setattr(main, "get_settings", Mock(side_effect=RuntimeError(marker)))
    args = main.build_parser().parse_args([command])
    assert args.func(args) == 1
    output = capsys.readouterr()
    assert marker not in output.out + output.err


def test_source_collector_stays_disabled_by_default(monkeypatch):
    monkeypatch.delenv("SOURCE_INTAKE_ENABLED", raising=False)
    assert Settings(_env_file=None).source_intake_enabled is False


def test_health_still_constructs_clients_only_when_requested(monkeypatch):
    from etl.load import db

    engine = object()
    client = SimpleNamespace(health_check=Mock(return_value={"status": "fixture"}))
    make_engine = Mock(return_value=engine)
    make_client = Mock(return_value=client)
    monkeypatch.setattr(orchestrator, "create_db_engine", make_engine)
    monkeypatch.setattr(orchestrator, "get_redcap_client", make_client)
    database_check = Mock(return_value=True)
    monkeypatch.setattr(db, "check_database", database_check)
    instance = orchestrator.SyncOrchestrator(Settings(_env_file=None))
    make_engine.assert_not_called()
    make_client.assert_not_called()
    assert instance.health()["database"] is True
    make_engine.assert_called_once()
    make_client.assert_called_once()
    database_check.assert_called_once_with(engine)
