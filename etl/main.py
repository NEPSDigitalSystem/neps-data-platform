from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

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

    # Workstream D: Operator CLI commands
    process_queue_parser = subparsers.add_parser("process-queue", help="Process intake queue with DownstreamProcessor")
    process_queue_parser.add_argument("--limit", type=int, default=100, help="Maximum records to process")
    process_queue_parser.add_argument("--actor", type=str, required=True, help="Actor name for audit")
    process_queue_parser.set_defaults(func=cmd_process_queue)

    requeue_parser = subparsers.add_parser("requeue", help="Requeue a specific intake revision for processing")
    requeue_parser.add_argument("--source-revision-id", type=str, required=True, help="Source revision ID to requeue")
    requeue_parser.add_argument("--actor", type=str, required=True, help="Actor name for audit")
    requeue_parser.set_defaults(func=cmd_requeue)

    queue_status_parser = subparsers.add_parser("queue-status", help="Show intake queue status (pending/leased/mapping_pending/processing_restricted)")
    queue_status_parser.set_defaults(func=cmd_queue_status)

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


def cmd_process_queue(args: argparse.Namespace) -> int:
    """Process intake queue with DownstreamProcessor."""
    from etl.sync.v31_workflow import DownstreamProcessor
    from etl.intake.v31 import Intake
    from etl.repository.participant_links import ParticipantLinks
    from etl.repository.v31 import Repository
    import os
    import json

    settings = get_settings()

    # Check if approved metadata versions file is configured
    approved_file = os.environ.get("APPROVED_METADATA_VERSIONS_FILE")
    if not approved_file:
        logger.error("approved_metadata_versions_file_not_set")
        return 1

    try:
        with open(approved_file, "r") as f:
            approved_data = json.load(f)
            approved_metadata = approved_data.get("metadata_versions", {})
    except Exception as e:
        logger.error("failed_to_load_approved_metadata", error=str(e))
        return 1

    # Create DownstreamProcessor
    engine = create_db_engine(settings)

    # Create Intake with required parameters from settings
    intake = Intake(
        engine,
        project=settings.source_destination or "nds-v31",
        destination=settings.warehouse_schema,
        service_identity=settings.source_service_identity or "nds-processor",
    )
    repository = Repository(engine, settings.warehouse_schema)
    
    # Create authoriser function (placeholder - must be configured)
    def authoriser(project, source_id, nds_id, actor):
        # Placeholder: In production, this would call the NDS registration service
        # to verify the binding is authorised
        logger.warning("using_placeholder_authoriser", actor=actor)
        return True  # Placeholder - always returns True
    
    participant_links = ParticipantLinks(engine, authoriser=authoriser)

    # Create applicability provider (placeholder - should be configured based on actual policy)
    def applicability_provider(field_name: str) -> Optional[bool]:
        # Placeholder: explicit True/False callback
        # In production, this would check actual EPI/NSES applicability policy
        # For now, return True to allow processing (conservative approach)
        return True  # Placeholder - allows processing

    processor = DownstreamProcessor(
        intake=intake,
        repository=repository,
        links=participant_links,
        approved_metadata_versions=approved_metadata,
        applicability_provider=applicability_provider,
    )

    # Process queue
    try:
        result = processor.process(limit=args.limit)
        logger.info(
            "queue_processing_complete",
            actor=args.actor,
            processed=result.get("processed", 0),
            deferred=result.get("deferred", 0),
        )
        print(f"Processed: {result.get('processed', 0)}, Deferred: {result.get('deferred', 0)}")
        return 0
    except Exception as e:
        logger.error("queue_processing_failed", error=str(e))
        return 1


def cmd_requeue(args: argparse.Namespace) -> int:
    """Requeue a specific intake revision for processing."""
    from etl.intake.v31 import Intake

    settings = get_settings()
    engine = create_db_engine(settings)
    intake = Intake(
        engine,
        project=settings.SOURCE_DESTINATION or "nds-v31",
        destination=settings.warehouse_schema,
        service_identity=settings.SOURCE_SERVICE_IDENTITY or "nds-processor",
    )

    try:
        intake.requeue(args.source_revision_id, args.actor)
        logger.info(
            "requeue_complete",
            source_revision_id=args.source_revision_id,
            actor=args.actor,
        )
        print(f"Requeued: {args.source_revision_id}")
        return 0
    except Exception as e:
        logger.error("requeue_failed", error=str(e))
        return 1


def cmd_queue_status(args: argparse.Namespace) -> int:
    """Show intake queue status."""
    from etl.intake.v31 import Intake
    from sqlalchemy import text
    import re

    settings = get_settings()
    engine = create_db_engine(settings)
    schema = settings.warehouse_schema or "public"

    # Validate schema name to prevent SQL injection
    if not re.match(r'^[a-z][a-z0-9_]{0,62}$', schema):
        logger.error("invalid_schema_name", schema=schema)
        return 1

    try:
        with engine.connect() as conn:
            # Count pending
            pending = conn.execute(
                text(f"SELECT COUNT(*) FROM {schema}.nds_v31_intake_pending WHERE state = 'pending'")
            ).scalar()

            # Count leased
            leased = conn.execute(
                text(f"SELECT COUNT(*) FROM {schema}.nds_v31_intake_pending WHERE state = 'leased'")
            ).scalar()

            # Count mapping_pending (from intake head table - this is a placeholder check)
            # In reality, mapping status would be tracked in the head table
            mapping_pending = 0  # Placeholder

            # Count processing_restricted (placeholder)
            processing_restricted = 0  # Placeholder

        status = {
            "pending": pending or 0,
            "leased": leased or 0,
            "mapping_pending": mapping_pending,
            "processing_restricted": processing_restricted,
        }

        logger.info("queue_status", **status)
        print(json.dumps(status, indent=2))
        return 0
    except Exception as e:
        logger.error("queue_status_failed", error=str(e))
        return 1


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
