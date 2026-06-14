from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from etl.models.metadata import InstrumentDefinition, MetadataModel
from etl.transform.parser import prepare_row, record_conflict_keys


def _sql_type(field_type: str) -> str:
    mapping = {
        "integer": "INTEGER",
        "float": "DOUBLE PRECISION",
        "date": "DATE",
        "datetime": "TIMESTAMP",
    }
    return mapping.get(field_type, "TEXT")


def table_name(instrument_name: str) -> str:
    return instrument_name


def view_name(instrument_name: str) -> str:
    return f"v_{instrument_name}"


def persist_metadata(
    connection: Connection,
    metadata: MetadataModel,
    *,
    project_id: str,
) -> None:
    connection.execute(
        text(
            """
            INSERT INTO redcap.raw_redcap_metadata (project_id, metadata_json, metadata_hash, source_mode)
            VALUES (:project_id, CAST(:metadata_json AS JSONB), :metadata_hash, :source_mode)
            ON CONFLICT (project_id)
            DO UPDATE SET
                metadata_json = EXCLUDED.metadata_json,
                metadata_hash = EXCLUDED.metadata_hash,
                source_mode = EXCLUDED.source_mode,
                updated_at = NOW()
            """
        ),
        {
            "project_id": project_id,
            "metadata_json": json.dumps(metadata.raw),
            "metadata_hash": metadata.metadata_hash(),
            "source_mode": metadata.source_mode,
        },
    )


def _insert_shape(
    instrument_name: str,
    columns: list[str],
) -> tuple[list[str], list[str]]:
    insert_columns = list(columns)
    value_expressions = [f":{col}" for col in columns]

    if instrument_name == "consent_records" and "participant_id" not in insert_columns:
        insert_columns.insert(0, "participant_id")
        value_expressions.insert(
            0,
            "(SELECT id FROM redcap.participants WHERE record_id = :record_id)",
        )

    return insert_columns, value_expressions


def upsert_rows(
    connection: Connection,
    instrument: InstrumentDefinition,
    rows: list[dict[str, Any]],
) -> int:
    if not rows:
        return 0

    field_order = [field.field_name for field in instrument.fields]
    columns = [col for col in field_order if any(col in row for row in rows)]
    rows = [{col: row.get(col) for col in columns} for row in rows]

    conflict_keys = record_conflict_keys(instrument)
    rows = [
        row
        for row in rows
        if all(row.get(key) not in (None, "") for key in conflict_keys)
    ]
    if not rows:
        return 0

    insert_columns, value_expressions = _insert_shape(instrument.instrument_name, columns)
    update_columns = [col for col in insert_columns if col not in conflict_keys and col != "created_at"]

    assignments = [f"{col} = EXCLUDED.{col}" for col in update_columns]
    if instrument.instrument_name == "participants":
        assignments.append("updated_at = NOW()")

    col_sql = ", ".join(insert_columns)
    value_sql = ", ".join(value_expressions)
    conflict_sql = ", ".join(conflict_keys)

    if assignments:
        conflict_action = f"DO UPDATE SET {', '.join(assignments)}"
    else:
        conflict_action = "DO NOTHING"

    sql = f"""
        INSERT INTO redcap.{table_name(instrument.instrument_name)} ({col_sql})
        VALUES ({value_sql})
        ON CONFLICT ({conflict_sql})
        {conflict_action}
    """

    for row in rows:
        connection.execute(text(sql), row)

    return len(rows)


def load_instrument_records(
    engine: Engine,
    instrument: InstrumentDefinition,
    records: list[dict[str, Any]],
    *,
    synced_at: str,
    etl_run_id: str,
    source_mode: str,
) -> int:
    rows = [
        prepare_row(
            record,
            instrument,
            synced_at=synced_at,
            etl_run_id=etl_run_id,
            source_mode=source_mode,
        )
        for record in records
    ]
    with engine.begin() as connection:
        return upsert_rows(connection, instrument, rows)


def refresh_views(engine: Engine, metadata: MetadataModel) -> None:
    with engine.begin() as connection:
        for instrument in metadata.instruments:
            if not instrument.fields:
                continue

            select_parts = []
            for field in instrument.fields:
                if field.choices:
                    case_parts = " ".join(
                        f"WHEN {table_name(instrument.instrument_name)}.{field.field_name} = '{code}' "
                        f"THEN '{label}'"
                        for code, label in field.choices.items()
                    )
                    select_parts.append(
                        f"CASE {case_parts} ELSE {table_name(instrument.instrument_name)}.{field.field_name}::text END AS {field.field_name}"
                    )
                else:
                    select_parts.append(field.field_name)

            select_sql = ", ".join(select_parts)
            connection.execute(
                text(
                    f"""
                    CREATE OR REPLACE VIEW redcap.{view_name(instrument.instrument_name)} AS
                    SELECT {select_sql}
                    FROM redcap.{table_name(instrument.instrument_name)}
                    """
                )
            )
