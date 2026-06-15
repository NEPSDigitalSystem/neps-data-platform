from __future__ import annotations

from typing import Any

from etl.models.metadata import FieldDefinition, InstrumentDefinition, MetadataModel
from etl.transform.mock_schema import get_mock_instruments


def normalize_metadata(raw: Any, *, source_mode: str) -> MetadataModel:
    if source_mode == "mock":
        if not isinstance(raw, dict):
            raise ValueError("Mock metadata must be a JSON object")
        instruments = get_mock_instruments()
        return MetadataModel(
            project_id=str(raw.get("project_id", "NEPS-2025")),
            project_title=str(raw.get("project_title", "NEPS Digital")),
            instruments=instruments,
            events=list(raw.get("events", [])),
            raw=raw,
            source_mode="mock",
        )

    if not isinstance(raw, list):
        raise ValueError("Production metadata must be a list of field definitions")

    instruments_map: dict[str, InstrumentDefinition] = {}
    for field_row in raw:
        form_name = str(field_row.get("form_name", "unknown"))
        if form_name not in instruments_map:
            instruments_map[form_name] = InstrumentDefinition(
                instrument_name=form_name,
                instrument_label=str(field_row.get("form_name", form_name)),
                repeating=False,
                fields=[],
            )

        choices: dict[str, str] = {}
        select_choices = field_row.get("select_choices_or_calculations")
        if isinstance(select_choices, str) and select_choices.strip():
            for part in select_choices.split("|"):
                if "," in part:
                    code, label = part.split(",", 1)
                    choices[code.strip()] = label.strip()

        instruments_map[form_name].fields.append(
            FieldDefinition(
                field_name=str(field_row.get("field_name", "")),
                field_type=str(field_row.get("field_type", "text")),
                field_label=str(field_row.get("field_label", "")),
                choices=choices,
            )
        )

    return MetadataModel(
        project_id="production",
        project_title="REDCap Production Project",
        instruments=list(instruments_map.values()),
        events=[],
        raw={"fields": raw},
        source_mode="production",
    )
