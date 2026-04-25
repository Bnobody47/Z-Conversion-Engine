from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_hiring_signals(
    *,
    company_name: str,
    funding_event: dict[str, Any],
    job_velocity: dict[str, Any],
    layoff_event: dict[str, Any],
    leadership_event: dict[str, Any],
) -> dict[str, Any]:
    """
    Merge the four hiring-signal sources into a structured brief payload.
    """
    return {
        "prospect_name": company_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "signals": {
            "funding_event": funding_event,
            "job_post_velocity": job_velocity,
            "layoff_event": layoff_event,
            "leadership_change": leadership_event,
        },
        "signal_confidence": {
            "funding_event": funding_event.get("confidence_score", 0.5),
            "job_post_velocity": job_velocity.get("confidence_score", 0.5),
            "layoff_event": layoff_event.get("confidence_score", 0.5),
            "leadership_change": leadership_event.get("confidence_score", 0.5),
        },
        "source_attribution": {
            "funding_event": funding_event.get("source_url", ""),
            "job_post_velocity": job_velocity.get("sources", []),
            "layoff_event": layoff_event.get("source_url", ""),
            "leadership_change": leadership_event.get("source_url", ""),
        },
    }
