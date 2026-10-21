"""Minimal V3.1 baseline ingestion from the mock REDCap source into storage.

Fetches the V3.1 baseline screening dataset, writes each revision to
``nds_v31_source`` and stores the authoritative V3.1 scores in
``nds_v31_derived``. This is the operator path behind ``ingest-v31``; richer
reconciliation and registry/consent gating remain in the intake workflow.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog
from sqlalchemy import text
from sqlalchemy.engine import Engine

from etl.config import Settings, get_settings
from etl.extract.mock_client import MockRedcapClient
from etl.scoring.v31 import Scorer

logger = structlog.get_logger(__name__)

CONTRACT_PATH = Path(__file__).parent / "contracts" / "data_contract_v31.json"


def load_v31_contract() -> dict[str, Any]:
    """Load the V3.1 data contract that travels with this package."""
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def ingest_v31_baseline(settings: Settings, engine: Engine) -> dict[str, Any]:
    """Ingest V3.1 baseline data from the mock REDCap source into storage."""
    if not settings.source_destination:
        raise ValueError("SOURCE_DESTINATION is required to store V3.1 baseline revisions")

    v31_contract = load_v31_contract()
    contract_hash = hashlib.sha256(json.dumps(v31_contract, sort_keys=True).encode()).hexdigest()

    baseline_data = MockRedcapClient(settings).export_v31_baseline()
    records = baseline_data.get("data", [])
    logger.info("fetched_v31_data", count=len(records))

    if not records:
        logger.warning("no_v31_records_found")
        return {"status": "success", "received": 0, "scored": 0, "metadata_sha256": contract_hash}

    scorer = Scorer(v31_contract)
    observed_at = datetime.now(timezone.utc).isoformat()

    received_count = 0
    with engine.begin() as conn:
        for record in records:
            study_id = record.get("study_id")
            if not study_id:
                logger.warning("record_missing_study_id")
                continue

            record_id = f"v31_{study_id}"
            conn.execute(
                text("""
                    INSERT INTO nds_v31_source
                    (id, identity_key, identity, revision, change_hash, source_version,
                     contract_version, payload, country, observed_at, contract_hash,
                     storage_destination)
                    VALUES
                    (:id, :identity_key, :identity, :revision, :change_hash, :source_version,
                     :contract_version, :payload, :country, :observed_at, :contract_hash,
                     :storage_destination)
                    ON CONFLICT (identity_key, storage_destination, revision) DO NOTHING
                """),
                {
                    "id": record_id,
                    "identity_key": f"{settings.redcap_project_id}:{study_id}:baseline_arm_1:neps31_screening:",
                    "identity": json.dumps({
                        "project": settings.redcap_project_id,
                        "participant": study_id,
                        "event": "baseline_arm_1",
                        "instrument": "neps31_screening",
                        "instance": "",
                    }),
                    "revision": 1,
                    "change_hash": hashlib.sha256(
                        json.dumps(record, sort_keys=True).encode()).hexdigest(),
                    "source_version": "v31-mock-api",
                    "contract_version": v31_contract["contract_version"],
                    "payload": json.dumps(record),
                    "country": record.get("country", "Unknown"),
                    "observed_at": observed_at,
                    "contract_hash": contract_hash,
                    "storage_destination": settings.source_destination,
                },
            )
            received_count += 1

    scored_count = 0
    with engine.begin() as conn:
        for record in records:
            study_id = record.get("study_id")
            if not study_id:
                continue

            scoring_result = scorer.score(record)
            scores = {
                name: None if score.value is None else float(score.value)
                for name, score in scoring_result.scores.items()
            }

            conn.execute(
                text("""
                    INSERT INTO nds_v31_derived
                    (id, source_id, calculation_version, result)
                    VALUES
                    (:id, :source_id, :calculation_version, :result)
                    ON CONFLICT (source_id, calculation_version) DO UPDATE SET result = :result
                """),
                {
                    "id": f"scored_v31_{study_id}",
                    "source_id": f"v31_{study_id}",
                    "calculation_version": scoring_result.algorithm_version,
                    "result": json.dumps(scores),
                },
            )
            scored_count += 1

    logger.info("v31_ingestion_complete", received=received_count, scored=scored_count)
    return {
        "status": "success",
        "received": received_count,
        "scored": scored_count,
        "metadata_sha256": contract_hash,
    }


if __name__ == "__main__":
    from etl.load.db import create_db_engine

    print(json.dumps(ingest_v31_baseline(get_settings(), create_db_engine(get_settings())), indent=2))
