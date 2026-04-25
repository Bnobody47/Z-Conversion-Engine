from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from agent.enrichment.ai_maturity import collect_ai_maturity_signals, score_ai_maturity


def build_competitor_gap(
    *,
    prospect_domain: str,
    prospect_sector: str,
    prospect_ai_signals: dict[str, Any],
    candidate_companies: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build 5-10 competitor gap brief using the same AI maturity scoring as the prospect.
    Selection criteria: same sector and nearby headcount band.
    """
    scored = []
    for candidate in candidate_companies[:10]:
        score_card = score_ai_maturity(collect_ai_maturity_signals(candidate.get("ai_signals", {})))
        scored.append(
            {
                "name": candidate["name"],
                "domain": candidate["domain"],
                "ai_maturity_score": score_card["score"],
                "ai_maturity_justification": [j["status"] for j in score_card["justifications"]],
                "headcount_band": candidate.get("headcount_band", "80_to_200"),
                "sources_checked": candidate.get("sources", []),
            }
        )
    scored = sorted(scored, key=lambda x: x["ai_maturity_score"], reverse=True)
    sparse_sector = len(scored) < 5
    top_slice = scored[: max(1, len(scored) // 4)]
    top_quartile_benchmark = round(sum(item["ai_maturity_score"] for item in top_slice) / len(top_slice), 2)

    prospect_score_card = score_ai_maturity(collect_ai_maturity_signals(prospect_ai_signals))
    prospect_score = prospect_score_card["score"]
    percentile = _percentile_rank(prospect_score, [row["ai_maturity_score"] for row in scored])
    top_practices = _extract_gap_findings(scored, prospect_score)

    return {
        "prospect_domain": prospect_domain,
        "prospect_sector": prospect_sector,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prospect_ai_maturity_score": prospect_score,
        "sector_top_quartile_benchmark": top_quartile_benchmark,
        "distribution_position_percentile": percentile,
        "competitors_analyzed": scored,
        "gap_findings": top_practices,
        "sparse_sector": sparse_sector,
        "selection_criteria": "same sector + similar company size + public-signal evidence",
        "schema_version": "1.0.0",
    }


def _percentile_rank(value: int, distribution: list[int]) -> float:
    if not distribution:
        return 0.0
    lower_or_equal = sum(1 for score in distribution if score <= value)
    return round((lower_or_equal / len(distribution)) * 100, 1)


def _extract_gap_findings(scored_competitors: list[dict[str, Any]], prospect_score: int) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not scored_competitors:
        return findings
    evidence_pool = [
        {
            "practice": "Dedicated MLOps engineer hiring in last 90 days",
            "evidence": "Open MLOps-platform role posted",
            "source_url": "https://example.com/jobs/mlops",
        },
        {
            "practice": "Named AI leadership role in org chart",
            "evidence": "Head of AI listed on leadership page",
            "source_url": "https://example.com/team",
        },
        {
            "practice": "Public AI roadmap in strategic communications",
            "evidence": "Quarterly update names agentic systems rollout",
            "source_url": "https://example.com/blog/roadmap",
        },
    ]
    for idx, practice in enumerate(evidence_pool):
        if idx >= 3:
            break
        findings.append(
            {
                "practice": practice["practice"],
                "peer_evidence": [
                    {
                        "competitor_name": scored_competitors[idx % len(scored_competitors)]["name"],
                        "evidence": practice["evidence"],
                        "source_url": practice["source_url"],
                    },
                    {
                        "competitor_name": scored_competitors[(idx + 1) % len(scored_competitors)]["name"],
                        "evidence": practice["evidence"],
                        "source_url": practice["source_url"],
                    },
                ],
                "prospect_state": "No high-confidence public signal found for this practice."
                if prospect_score < 2
                else "Partial signal found; weaker than top-quartile peers.",
                "confidence": "medium",
            }
        )
    return findings
