from __future__ import annotations

import json
import random
import statistics
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=True) + "\n")


class ProspectIn(BaseModel):
    company_name: str
    website: str | None = None
    email: str
    phone: str | None = None
    country: str = "US"
    synthetic: bool = True


class InboundMessage(BaseModel):
    lead_id: str
    channel: str = Field(pattern="^(email|sms)$")
    message: str


def _ai_maturity_score(signals: dict[str, Any]) -> dict[str, Any]:
    score = 0
    justification = []

    if signals["ai_roles_open"] >= 3:
        score += 1
        justification.append(">=3 AI-adjacent open roles")
    if signals["named_ai_leader"]:
        score += 1
        justification.append("Named AI leadership found")
    if signals["exec_ai_mentions_last_12m"]:
        score += 1
        justification.append("Executive AI commentary in last 12 months")

    confidence = "high" if len(justification) >= 2 else "medium" if justification else "low"
    return {"score": min(score, 3), "confidence": confidence, "justification": justification}


def build_hiring_signal_brief(company_name: str) -> dict[str, Any]:
    # Synthetic but reproducible signals for local development.
    seed = abs(hash(company_name)) % 10000
    rng = random.Random(seed)

    funding_raised_180d = rng.choice([True, False, True])
    job_posts_now = rng.randint(2, 20)
    job_posts_60d = max(1, job_posts_now - rng.randint(0, 8))
    layoffs_120d = rng.choice([True, False, False])
    leadership_change_90d = rng.choice([True, False])

    signals = {
        "funding_event_180d": funding_raised_180d,
        "job_post_velocity_60d": round((job_posts_now - job_posts_60d) / max(job_posts_60d, 1), 2),
        "open_engineering_roles": job_posts_now,
        "ai_roles_open": rng.randint(0, 5),
        "named_ai_leader": rng.choice([True, False]),
        "exec_ai_mentions_last_12m": rng.choice([True, False]),
        "layoffs_120d": layoffs_120d,
        "leadership_change_90d": leadership_change_90d,
    }
    maturity = _ai_maturity_score(signals)

    return {
        "company_name": company_name,
        "generated_at": _utc_now_iso(),
        "signals": signals,
        "ai_maturity": maturity,
        "segment_guess": _segment_guess(signals),
    }


def _segment_guess(signals: dict[str, Any]) -> str:
    if signals["funding_event_180d"] and not signals["layoffs_120d"]:
        return "segment_1_recently_funded"
    if signals["layoffs_120d"]:
        return "segment_2_restructuring"
    if signals["leadership_change_90d"]:
        return "segment_3_engineering_transition"
    return "segment_4_specialized_capability_gap"


def build_competitor_gap_brief(company_name: str, ai_maturity: int) -> dict[str, Any]:
    competitor_scores = [2, 2, 3, 1, 3, 2]
    top_quartile_practices = [
        "Published platform engineering roadmap with AI milestones",
        "Dedicated ML infrastructure role with hiring velocity > 2/month",
        "Quarterly engineering productivity and quality scorecard",
    ]
    percentile = round((sum(s <= ai_maturity for s in competitor_scores) / len(competitor_scores)) * 100, 1)
    return {
        "company_name": company_name,
        "generated_at": _utc_now_iso(),
        "sector_peer_count": len(competitor_scores),
        "prospect_ai_maturity_score": ai_maturity,
        "sector_percentile": percentile,
        "top_quartile_practices_missing": top_quartile_practices[:2 if ai_maturity < 2 else 1],
        "confidence": "medium",
    }


def _qualify_lead(hiring_brief: dict[str, Any]) -> dict[str, Any]:
    signals = hiring_brief["signals"]
    score = 0
    if signals["funding_event_180d"]:
        score += 2
    if signals["open_engineering_roles"] >= 8:
        score += 2
    if signals["leadership_change_90d"]:
        score += 1
    if signals["layoffs_120d"]:
        score += 1

    qualified = score >= 4
    return {
        "qualified": qualified,
        "qualification_score": score,
        "reason": "Strong external signals" if qualified else "Insufficient buying-window confidence",
    }


def _book_cal_slot(lead_id: str) -> dict[str, Any]:
    start = datetime.now(timezone.utc) + timedelta(days=2)
    booking = {
        "booking_id": f"cal_{uuid.uuid4().hex[:8]}",
        "lead_id": lead_id,
        "start_time_utc": start.replace(minute=0, second=0, microsecond=0).isoformat(),
        "attendees": ["prospect@synthetic.local", "delivery-lead@tenacious.local"],
        "created_at": _utc_now_iso(),
    }
    _append_jsonl(DATA_DIR / "cal_bookings.jsonl", booking)
    return booking


def _hubspot_write(event_type: str, lead_id: str, payload: dict[str, Any]) -> None:
    record = {
        "event_id": f"hs_{uuid.uuid4().hex[:10]}",
        "event_type": event_type,
        "lead_id": lead_id,
        "payload": payload,
        "written_at": _utc_now_iso(),
    }
    _append_jsonl(DATA_DIR / "hubspot_events.jsonl", record)


def _trace_interaction(lead_id: str, channel: str, latency_ms: int, metadata: dict[str, Any]) -> None:
    trace = {
        "trace_id": f"tr_{uuid.uuid4().hex[:10]}",
        "lead_id": lead_id,
        "channel": channel,
        "latency_ms": latency_ms,
        "timestamp": _utc_now_iso(),
        "metadata": metadata,
    }
    _append_jsonl(DATA_DIR / "interaction_traces.jsonl", trace)


app = FastAPI(title="Z Conversion Engine", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "time": _utc_now_iso()}


@app.post("/leads/process")
def process_lead(prospect: ProspectIn) -> dict[str, Any]:
    lead_id = f"lead_{uuid.uuid4().hex[:10]}"

    hiring_signal_brief = build_hiring_signal_brief(prospect.company_name)
    competitor_gap_brief = build_competitor_gap_brief(
        prospect.company_name, hiring_signal_brief["ai_maturity"]["score"]
    )
    qualification = _qualify_lead(hiring_signal_brief)

    lead_record = {
        "lead_id": lead_id,
        "prospect": prospect.model_dump(),
        "hiring_signal_brief": hiring_signal_brief,
        "competitor_gap_brief": competitor_gap_brief,
        "qualification": qualification,
        "created_at": _utc_now_iso(),
    }
    _append_jsonl(DATA_DIR / "leads.jsonl", lead_record)
    _hubspot_write("lead_enriched", lead_id, lead_record)

    latency_ms = random.randint(1300, 5900)
    _trace_interaction(lead_id, "email", latency_ms, {"stage": "initial_enrichment"})

    booking = None
    if qualification["qualified"]:
        booking = _book_cal_slot(lead_id)
        _hubspot_write("meeting_booked", lead_id, booking)

    return {"lead_id": lead_id, "qualified": qualification["qualified"], "booking": booking}


@app.post("/webhooks/inbound")
def inbound_message(message: InboundMessage) -> dict[str, Any]:
    if message.channel not in {"email", "sms"}:
        raise HTTPException(status_code=400, detail="Unsupported channel")

    body = message.message.strip().lower()
    if body in {"stop", "unsubscribe", "uns"}:
        _hubspot_write("consent_revoked", message.lead_id, {"channel": message.channel})
        _trace_interaction(message.lead_id, message.channel, 950, {"action": "opt_out"})
        return {"status": "opted_out", "reply": "You have been unsubscribed. Reply START to opt back in."}

    if body == "help":
        _trace_interaction(message.lead_id, message.channel, 880, {"action": "help"})
        return {"status": "ok", "reply": "Reply STOP to unsubscribe. For urgent help, email support@tenacious.local"}

    reply = (
        "Thanks for the reply. I can share a short benchmark brief and book a 30-minute "
        "discovery call with a Tenacious delivery lead."
    )
    latency_ms = random.randint(1100, 4100)
    _trace_interaction(message.lead_id, message.channel, latency_ms, {"action": "nurture_reply"})
    _hubspot_write("conversation_event", message.lead_id, {"channel": message.channel, "message": message.message})
    return {"status": "ok", "reply": reply}


@app.get("/metrics/latency")
def latency_summary() -> dict[str, float | int]:
    trace_path = DATA_DIR / "interaction_traces.jsonl"
    if not trace_path.exists():
        return {"count": 0, "p50_ms": 0, "p95_ms": 0}

    values = []
    with trace_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            values.append(json.loads(line)["latency_ms"])
    if not values:
        return {"count": 0, "p50_ms": 0, "p95_ms": 0}

    values_sorted = sorted(values)
    p50 = values_sorted[len(values_sorted) // 2]
    p95 = values_sorted[int(len(values_sorted) * 0.95) - 1]
    return {
        "count": len(values),
        "p50_ms": p50,
        "p95_ms": p95,
        "mean_ms": round(statistics.mean(values), 2),
    }
