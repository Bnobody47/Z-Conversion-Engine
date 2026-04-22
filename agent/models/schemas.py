from __future__ import annotations

from pydantic import BaseModel


class LeadBrief(BaseModel):
    lead_id: str
    company_name: str
    segment_guess: str
    confidence: str
