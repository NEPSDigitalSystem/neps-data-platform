"""Retired distress analysis entry point, retained for older callers.

The data engineer approved retirement on 15 October 2026. The old threshold
had no scientific approval and the writer replaced or dropped results. Existing
warehouse records are preserved. Reviewed analysis belongs to later delivery.
"""
from __future__ import annotations

from etl.config import Settings


def analyze_distress_trends(settings: Settings | None = None) -> None:
    raise PermissionError(
        "Legacy distress analysis disabled: retired pending reviewed analysis"
    )
