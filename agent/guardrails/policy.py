from __future__ import annotations


def check_overclaim_risk(confidence: str, draft_message: str) -> dict:
    """
    Basic hook for confidence-aware phrasing checks.
    """
    risky = confidence == "low" and any(k in draft_message.lower() for k in ["definitely", "certainly", "guaranteed"])
    return {"allow": not risky, "reason": "low-confidence overclaim" if risky else "ok"}
