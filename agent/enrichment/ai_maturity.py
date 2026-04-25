from __future__ import annotations

from dataclasses import dataclass
from typing import Any


HIGH_WEIGHT = 3
MEDIUM_WEIGHT = 2
LOW_WEIGHT = 1


@dataclass
class SignalInput:
    key: str
    detected: bool
    evidence: str
    weight: int
    confidence: float


def collect_ai_maturity_signals(raw: dict[str, Any]) -> list[SignalInput]:
    """
    Collect all six required AI-maturity categories.
    """
    return [
        SignalInput(
            key="ai_adjacent_open_roles",
            detected=bool(raw.get("ai_roles_open", 0) > 0),
            evidence=f"AI-adjacent open roles={raw.get('ai_roles_open', 0)}",
            weight=HIGH_WEIGHT,
            confidence=min(1.0, 0.4 + 0.1 * int(raw.get("ai_roles_open", 0))),
        ),
        SignalInput(
            key="named_ai_ml_leadership",
            detected=bool(raw.get("named_ai_leader", False)),
            evidence="Named AI/ML leadership found" if raw.get("named_ai_leader", False) else "No named AI/ML leader found",
            weight=HIGH_WEIGHT,
            confidence=0.8 if raw.get("named_ai_leader", False) else 0.45,
        ),
        SignalInput(
            key="github_org_activity",
            detected=bool(raw.get("github_ai_activity", False)),
            evidence="Public GitHub activity on AI tooling detected" if raw.get("github_ai_activity", False) else "No public GitHub AI activity observed",
            weight=MEDIUM_WEIGHT,
            confidence=0.65 if raw.get("github_ai_activity", False) else 0.4,
        ),
        SignalInput(
            key="executive_commentary",
            detected=bool(raw.get("exec_ai_mentions_last_12m", False)),
            evidence="Executive AI commentary observed in last 12 months"
            if raw.get("exec_ai_mentions_last_12m", False)
            else "No executive AI commentary observed",
            weight=MEDIUM_WEIGHT,
            confidence=0.7 if raw.get("exec_ai_mentions_last_12m", False) else 0.45,
        ),
        SignalInput(
            key="modern_data_ml_stack",
            detected=bool(raw.get("modern_stack_detected", False)),
            evidence="Modern data/ML stack technologies observed" if raw.get("modern_stack_detected", False) else "No modern stack signal observed",
            weight=LOW_WEIGHT,
            confidence=0.6 if raw.get("modern_stack_detected", False) else 0.4,
        ),
        SignalInput(
            key="strategic_communications",
            detected=bool(raw.get("strategic_ai_comms", False)),
            evidence="Strategic communications reference AI priorities" if raw.get("strategic_ai_comms", False) else "No strategic communications AI signal observed",
            weight=LOW_WEIGHT,
            confidence=0.6 if raw.get("strategic_ai_comms", False) else 0.4,
        ),
    ]


def score_ai_maturity(signals: list[SignalInput]) -> dict[str, Any]:
    if not any(s.detected for s in signals):
        # Explicit silent-company handling required by rubric.
        return {
            "score": 0,
            "confidence": 0.35,
            "silent_company_note": "No public AI signal found; absence is not proof of absence.",
            "justifications": [to_justification(s) for s in signals],
        }

    weighted_detected = sum(s.weight for s in signals if s.detected)
    if weighted_detected >= 9:
        score = 3
    elif weighted_detected >= 6:
        score = 2
    elif weighted_detected >= 3:
        score = 1
    else:
        score = 0

    # Confidence is intentionally separate from score.
    confidence = round(sum(s.confidence for s in signals) / len(signals), 3)
    return {
        "score": score,
        "confidence": confidence,
        "silent_company_note": "",
        "justifications": [to_justification(s) for s in signals],
    }


def to_justification(signal: SignalInput) -> dict[str, Any]:
    return {
        "signal": signal.key,
        "status": signal.evidence,
        "weight": _weight_label(signal.weight),
        "confidence": _confidence_label(signal.confidence),
    }


def _weight_label(weight: int) -> str:
    if weight == HIGH_WEIGHT:
        return "high"
    if weight == MEDIUM_WEIGHT:
        return "medium"
    return "low"


def _confidence_label(value: float) -> str:
    if value >= 0.75:
        return "high"
    if value >= 0.5:
        return "medium"
    return "low"
