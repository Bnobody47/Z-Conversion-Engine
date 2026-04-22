from __future__ import annotations


def build_hiring_signals(company_name: str) -> dict:
    """
    Placeholder for funding, jobs, layoffs, and leadership change signals.
    """
    return {
        "company_name": company_name,
        "funding_event_180d": False,
        "job_post_velocity_60d": 0.0,
        "layoffs_120d": False,
        "leadership_change_90d": False,
        "confidence": "low",
    }
