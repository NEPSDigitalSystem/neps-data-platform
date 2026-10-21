from __future__ import annotations

import argparse
import json
import sys

import structlog
from alembic import command
from alembic.config import Config

from etl.config import get_settings
from etl.load.db import create_db_engine
from etl.sync.orchestrator import SyncOrchestrator

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NEPS REDCap ETL")
    subparsers = parser.add_subparsers(dest="command", required=True)

    health_parser = subparsers.add_parser("health", help="Check database and REDCap connectivity")
    health_parser.set_defaults(func=cmd_health)

    migrate_parser = subparsers.add_parser("migrate", help="Apply database migrations")
    migrate_parser.set_defaults(func=cmd_migrate)

    sync_parser = subparsers.add_parser("sync", help="Run REDCap sync")
    sync_parser.add_argument("--full", action="store_true", help="Full source reconciliation when collection is enabled")
    sync_parser.add_argument("--metadata-only", action="store_true", help="Retired legacy option; rejected by source intake")
    sync_parser.add_argument("--dry-run", action="store_true", help="Retired legacy option; rejected by source intake")
    sync_parser.set_defaults(func=cmd_sync)

    source_parser = subparsers.add_parser("collect-source", help="Receive all REDCap data independently of NDS registration/consent")
    source_parser.set_defaults(func=cmd_collect_source)

    v31_parser = subparsers.add_parser("ingest-v31", help="Ingest V3.1 baseline data from the mock REDCap source")
    v31_parser.set_defaults(func=cmd_ingest_v31)

    analyze_parser = subparsers.add_parser("analyze", help="Retired distress analysis; returns failure without data access")
    analyze_parser.set_defaults(func=cmd_analyze)

    return parser


def cmd_health(args: argparse.Namespace) -> int:
    settings = get_settings()
    orchestrator = SyncOrchestrator(settings)
    result = orchestrator.health()
    logger.info("health_check", **result)
    print(result)
    return 0 if result.get("database") else 1


def cmd_migrate(args: argparse.Namespace) -> int:
    settings = get_settings()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.attributes["database_url"] = settings.database_url
    alembic_cfg.attributes["warehouse_schema"] = settings.warehouse_schema
    command.upgrade(alembic_cfg, "head")
    logger.info("migrations_applied")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    try:
        settings = get_settings()
    except Exception:
        logger.error("source_configuration_failed", reason="configuration_unavailable")
        return 1
    if not settings.source_intake_enabled:
        logger.error("legacy_sync_disabled", reason="fixed_table_path_retired",
                     next_command="collect-source")
        return 1
    if args.metadata_only or args.dry_run:
        logger.error("source_options_rejected", reason="full_source_receipt_required")
        return 1
    return cmd_collect_source(args)


def cmd_collect_source(args: argparse.Namespace) -> int:
    from etl.sync.source_runtime import build_collector
    try:
        settings = get_settings()
        result = build_collector(settings).sync(source_version="native-api-metadata-snapshot")
    except Exception:
        logger.error("source_collection_failed", reason="source_service_or_store_unavailable")
        return 1
    logger.info("source_collection_completed", received=result['received'],
                metadata_sha256=result['metadata_sha256'], drift_count=len(result['contract_drift']))
    return 0


def cmd_ingest_v31(args: argparse.Namespace) -> int:
    from etl.ingest_v31_simple import ingest_v31_baseline
    try:
        settings = get_settings()
        result = ingest_v31_baseline(settings, create_db_engine(settings))
    except Exception:
        logger.error("v31_ingestion_failed", reason="source_or_store_unavailable")
        return 1
    logger.info("v31_ingestion_complete", **result)
    print(json.dumps(result, indent=2))
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    logger.error("legacy_analysis_disabled", reason="unapproved_distress_analysis_retired")
    return 1


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
