from __future__ import annotations

import argparse
import sys

import structlog
from alembic import command
from alembic.config import Config

from etl.config import get_settings
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
    sync_parser.add_argument("--full", action="store_true", help="Full refresh (default for mock mode)")
    sync_parser.add_argument("--metadata-only", action="store_true", help="Sync metadata only")
    sync_parser.add_argument("--dry-run", action="store_true", help="Extract metadata without loading records")
    sync_parser.set_defaults(func=cmd_sync)

    analyze_parser = subparsers.add_parser("analyze", help="Run data analysis and aggregations")
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
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_cfg, "head")
    logger.info("migrations_applied")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    settings = get_settings()
    orchestrator = SyncOrchestrator(settings)
    result = orchestrator.sync(
        full=args.full,
        metadata_only=args.metadata_only,
        dry_run=args.dry_run,
    )
    logger.info("sync_complete", **result)
    print(result)
    return 0 if result.get("status") in {"success", "dry_run"} else 1


def cmd_analyze(args: argparse.Namespace) -> int:
    settings = get_settings()
    from etl.analytics.distress_trends import analyze_distress_trends
    try:
        analyze_distress_trends(settings)
        return 0
    except Exception as e:
        logger.error("analysis_failed", error=str(e))
        return 1


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
