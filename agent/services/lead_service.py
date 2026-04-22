from __future__ import annotations

from agent.enrichment.crunchbase import lookup_company
from agent.enrichment.hiring_signals import build_hiring_signals


def enrich_lead(company_name: str) -> dict:
    return {
        "firmographics": lookup_company(company_name),
        "hiring_signals": build_hiring_signals(company_name),
    }
