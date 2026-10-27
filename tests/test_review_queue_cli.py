"""Tests for Workstream D: Review queue operator CLI commands.

Verifies:
- process-queue, requeue, queue-status CLI argument parsing
- Fail-closed behavior when APPROVED_METADATA_VERSIONS_FILE is missing/invalid
- Safe queue-status reporting without PHI/tokens
- Correct handling of DownstreamProcessor within CLI execution
"""
import argparse
import json
import os
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine

from etl.main import build_parser, cmd_process_queue, cmd_requeue, cmd_queue_status


def test_cli_parser_subcommands():
    parser = build_parser()
    
    # process-queue
    args = parser.parse_args(["process-queue", "--actor", "test-operator", "--limit", "50"])
    assert args.command == "process-queue"
    assert args.actor == "test-operator"
    assert args.limit == 50
    assert args.func == cmd_process_queue

    # requeue
    args = parser.parse_args(["requeue", "--source-revision-id", "REV-001", "--actor", "test-operator"])
    assert args.command == "requeue"
    assert args.source_revision_id == "REV-001"
    assert args.actor == "test-operator"
    assert args.func == cmd_requeue

    # queue-status
    args = parser.parse_args(["queue-status"])
    assert args.command == "queue-status"
    assert args.func == cmd_queue_status


def test_process_queue_fails_closed_without_approved_metadata_file(monkeypatch):
    monkeypatch.delenv("APPROVED_METADATA_VERSIONS_FILE", raising=False)
    args = argparse.Namespace(actor="test-operator", limit=10)
    ret = cmd_process_queue(args)
    assert ret == 1


def test_process_queue_fails_closed_with_missing_file(monkeypatch, tmp_path):
    missing_file = str(tmp_path / "non_existent_approved_metadata.json")
    monkeypatch.setenv("APPROVED_METADATA_VERSIONS_FILE", missing_file)
    args = argparse.Namespace(actor="test-operator", limit=10)
    ret = cmd_process_queue(args)
    assert ret == 1


def test_process_queue_fails_closed_with_corrupt_json(monkeypatch, tmp_path):
    corrupt_file = tmp_path / "corrupt_metadata.json"
    corrupt_file.write_text("NOT_JSON")
    monkeypatch.setenv("APPROVED_METADATA_VERSIONS_FILE", str(corrupt_file))
    args = argparse.Namespace(actor="test-operator", limit=10)
    ret = cmd_process_queue(args)
    assert ret == 1


def test_process_queue_with_approved_metadata(monkeypatch, tmp_path, capsys):
    approved_file = tmp_path / "approved_metadata.json"
    approved_file.write_text(json.dumps({
        "metadata_versions": {
            "test_hash": {
                "version": "v31-reviewed-test",
                "metadata": []
            }
        }
    }))
    monkeypatch.setenv("APPROVED_METADATA_VERSIONS_FILE", str(approved_file))
    
    mock_processor = MagicMock()
    mock_processor.process.return_value = {"processed": 5, "deferred": 2}

    with patch("etl.sync.v31_workflow.DownstreamProcessor", return_value=mock_processor):
        with patch("etl.main.create_db_engine"):
            args = argparse.Namespace(actor="test-operator", limit=10)
            ret = cmd_process_queue(args)
            assert ret == 0
            captured = capsys.readouterr()
            assert "Processed: 5, Deferred: 2" in captured.out


def test_queue_status_reports_counts(capsys):
    mock_engine = MagicMock()
    mock_engine.dialect.name = "postgresql"
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # 4 queries: pending, leased, mapping_pending, processing_restricted
    mock_conn.execute.return_value.scalar.side_effect = [12, 3, 4, 1]

    with patch("etl.main.create_db_engine", return_value=mock_engine):
        args = argparse.Namespace()
        ret = cmd_queue_status(args)
        assert ret == 0
        captured = capsys.readouterr()
        # Extract the json object from captured output (structlog prints first line)
        out_text = captured.out
        # find second {
        json_start = out_text.rfind("{\n")
        if json_start != -1:
            status = json.loads(out_text[json_start:])
        else:
            status = json.loads(out_text.splitlines()[-1])
        assert status == {
            "pending": 12,
            "leased": 3,
            "mapping_pending": 4,
            "processing_restricted": 1
        }


def test_requeue_calls_intake(capsys):
    mock_intake = MagicMock()
    with patch("etl.main.create_db_engine"):
        with patch("etl.intake.v31.Intake", return_value=mock_intake):
            args = argparse.Namespace(source_revision_id="REV-12345", actor="operator-1")
            ret = cmd_requeue(args)
            assert ret == 0
            mock_intake.requeue.assert_called_once_with("REV-12345", "operator-1")
            captured = capsys.readouterr()
            assert "Requeued: REV-12345" in captured.out
