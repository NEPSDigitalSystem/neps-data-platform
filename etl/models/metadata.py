from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldDefinition:
    field_name: str
    field_type: str = "text"
    field_label: str = ""
    choices: dict[str, str] = field(default_factory=dict)


@dataclass
class InstrumentDefinition:
    instrument_name: str
    instrument_label: str
    repeating: bool = False
    fields: list[FieldDefinition] = field(default_factory=list)


@dataclass
class MetadataModel:
    project_id: str
    project_title: str
    instruments: list[InstrumentDefinition]
    events: list[dict[str, Any]]
    raw: dict[str, Any] = field(default_factory=dict)
    source_mode: str = "mock"

    def metadata_hash(self) -> str:
        payload = {
            "project_id": self.project_id,
            "instruments": [
                {
                    "instrument_name": inst.instrument_name,
                    "fields": [f.field_name for f in inst.fields],
                }
                for inst in self.instruments
            ],
            "events": self.events,
        }
        encoded = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def get_instrument(self, name: str) -> InstrumentDefinition | None:
        return next((i for i in self.instruments if i.instrument_name == name), None)
