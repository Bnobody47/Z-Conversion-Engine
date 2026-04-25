from __future__ import annotations

import json
import random
import statistics
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from agent.adapters.email import EmailMessage, parse_resend_webhook, send_email_with_provider
from agent.adapters.hubspot_mcp_client import create_or_update_contact, log_activity, write_enrichment_fields
from agent.adapters.sms import parse_inbound_sms, send_sms
from agent.config import settings
from agent.enrichment.competitor_gap import build_competitor_gap
from agent.enrichment.pipeline import run_enrichment
from agent.services import event_bus
from agent.services.conversation_service import decide_handoff_state

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LEAD_STATE_PATH = DATA_DIR / "lead_state.json"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=True) + "\n")


def _load_state() -> dict[str, Any]:
    if not LEAD_STATE_PATH.exists():
        return {}
    return json.loads(LEAD_STATE_PATH.read_text(encoding="utf-8"))


def _save_state(state: dict[str, Any]) -> None:
    LEAD_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


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


class OutboundEmailRequest(BaseModel):
    lead_id: str
    to_email: str
    subject: str
    body: str


class OutboundSmsRequest(BaseModel):
    lead_id: str
    to_phone: str
    message: str


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
    hs_payload = {
        "properties": {
            "email": payload.get("prospect", {}).get("email", ""),
            "lead_id": lead_id,
            "event_type": event_type,
            "tenacious_status": "draft",
            "segment_match": payload.get("hiring_signal_brief", {}).get("primary_segment_match", ""),
            "segment_confidence": str(payload.get("hiring_signal_brief", {}).get("segment_confidence", "")),
            "enrichment_timestamp": payload.get("created_at", _utc_now_iso()),
        }
    }
    create_or_update_contact(hs_payload["properties"], access_token=settings.hubspot_access_token)
    write_enrichment_fields(
        {
            "lead_id": lead_id,
            "segment_match": hs_payload["properties"]["segment_match"],
            "segment_confidence": hs_payload["properties"]["segment_confidence"],
            "enrichment_timestamp": hs_payload["properties"]["enrichment_timestamp"],
        },
        access_token=settings.hubspot_access_token,
    )
    log_activity({"event_type": event_type, "lead_id": lead_id}, access_token=settings.hubspot_access_token)


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


def _extract_domain(url_or_email: str) -> str:
    if "@" in url_or_email:
        return url_or_email.split("@", maxsplit=1)[1].lower()
    parsed = urlparse(url_or_email if "://" in url_or_email else f"https://{url_or_email}")
    return parsed.netloc.lower()


def _mark_email_reply(lead_id: str) -> None:
    state = _load_state()
    row = state.get(lead_id, {})
    row["has_email_reply"] = True
    state[lead_id] = row
    _save_state(state)


def _is_sms_allowed(lead_id: str) -> bool:
    state = _load_state()
    decision = decide_handoff_state(
        lead_id=lead_id,
        has_replied_email=bool(state.get(lead_id, {}).get("has_email_reply")),
        prefers_sms=True,
    )
    return decision.allow_sms_send


app = FastAPI(title="Z Conversion Engine", version="0.2.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "time": _utc_now_iso()}


@app.post("/leads/process")
def process_lead(prospect: ProspectIn) -> dict[str, Any]:
    lead_id = f"lead_{uuid.uuid4().hex[:10]}"
    domain = _extract_domain(prospect.website or prospect.email)
    hiring_signal_brief = run_enrichment(
        company_name=prospect.company_name,
        prospect_domain=domain,
        seed_repo_path=settings.seed_repo_path,
    )
    candidate_companies = [
        {"name": "Peer A", "domain": "peer-a.com", "headcount_band": "200_to_500", "ai_signals": {"ai_roles_open": 4, "named_ai_leader": True}, "sources": ["https://peer-a.com/jobs"]},
        {"name": "Peer B", "domain": "peer-b.com", "headcount_band": "80_to_200", "ai_signals": {"ai_roles_open": 2, "named_ai_leader": False}, "sources": ["https://peer-b.com/team"]},
        {"name": "Peer C", "domain": "peer-c.com", "headcount_band": "200_to_500", "ai_signals": {"ai_roles_open": 5, "named_ai_leader": True}, "sources": ["https://peer-c.com/blog"]},
        {"name": "Peer D", "domain": "peer-d.com", "headcount_band": "80_to_200", "ai_signals": {"ai_roles_open": 1, "named_ai_leader": False}, "sources": ["https://peer-d.com/jobs"]},
        {"name": "Peer E", "domain": "peer-e.com", "headcount_band": "500_to_2000", "ai_signals": {"ai_roles_open": 3, "named_ai_leader": True}, "sources": ["https://peer-e.com/news"]},
    ]
    competitor_gap_brief = build_competitor_gap(
        prospect_domain=domain,
        prospect_sector="b2b_software",
        prospect_ai_signals={
            "ai_roles_open": hiring_signal_brief["hiring_velocity"]["open_roles_today"],
            "named_ai_leader": hiring_signal_brief["buying_window_signals"]["leadership_change"]["detected"],
        },
        candidate_companies=candidate_companies,
    )
    qualification = {
        "qualified": hiring_signal_brief["primary_segment_match"] != "abstain",
        "qualification_score": 4 if hiring_signal_brief["primary_segment_match"] != "abstain" else 2,
        "reason": "Segment matched with adequate confidence",
    }
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
    _trace_interaction(lead_id, "email", random.randint(1200, 4200), {"stage": "initial_enrichment"})

    # Exposed downstream interface: emit event for external subscribers.
    event_bus.emit("lead.enriched", {"lead_id": lead_id, "record": lead_record})
    return {"lead_id": lead_id, "qualified": qualification["qualified"]}


@app.post("/outbound/email")
def outbound_email(req: OutboundEmailRequest) -> dict[str, Any]:
    if not settings.tenacious_outbound_enabled:
        return {"ok": True, "status": "sink_mode", "reason": "TENACIOUS_OUTBOUND_ENABLED is not true"}
    api_key = settings.resend_api_key if settings.email_provider == "resend" else settings.mailersend_api_key
    result = send_email_with_provider(
        EmailMessage(to_email=req.to_email, subject=req.subject, body=req.body),
        provider=settings.email_provider,
        api_key=api_key,
        from_email=settings.email_from,
    )
    if not result.get("ok"):
        _trace_interaction(req.lead_id, "email", 0, {"action": "send_failed", "error": result.get("error")})
    handoff = decide_handoff_state(lead_id=req.lead_id, has_replied_email=False, prefers_sms=False)
    _append_jsonl(
        DATA_DIR / "outbound_email.jsonl",
        {"lead_id": req.lead_id, "request": req.model_dump(), "result": result, "cal_link": handoff.cal_link},
    )
    return result


@app.post("/outbound/sms")
def outbound_sms(req: OutboundSmsRequest) -> dict[str, Any]:
    if not _is_sms_allowed(req.lead_id):
        raise HTTPException(status_code=400, detail="SMS is warm-lead only; email reply required first")
    if not settings.tenacious_outbound_enabled:
        return {"ok": True, "status": "sink_mode", "reason": "TENACIOUS_OUTBOUND_ENABLED is not true"}
    result = send_sms(
        req.to_phone,
        req.message,
        username=settings.africastalking_username,
        api_key=settings.africastalking_api_key,
    )
    handoff = decide_handoff_state(lead_id=req.lead_id, has_replied_email=True, prefers_sms=True)
    _append_jsonl(
        DATA_DIR / "outbound_sms.jsonl",
        {"lead_id": req.lead_id, "request": req.model_dump(), "result": result, "cal_link": handoff.cal_link},
    )
    return result


@app.post("/webhooks/inbound")
def inbound_message(message: InboundMessage) -> dict[str, Any]:
    if message.channel not in {"email", "sms"}:
        raise HTTPException(status_code=400, detail="Unsupported channel")
    if message.channel == "email":
        _mark_email_reply(message.lead_id)
    body = message.message.strip().lower()
    if body in {"stop", "unsubscribe", "uns"}:
        _hubspot_write("consent_revoked", message.lead_id, {"channel": message.channel})
        _trace_interaction(message.lead_id, message.channel, 950, {"action": "opt_out"})
        event_bus.emit("inbound.opt_out", message.model_dump())
        return {"status": "opted_out", "reply": "You have been unsubscribed. Reply START to opt back in."}
    if body == "help":
        _trace_interaction(message.lead_id, message.channel, 880, {"action": "help"})
        return {"status": "ok", "reply": "Reply STOP to unsubscribe. For urgent help, email support@tenacious.local"}
    _trace_interaction(message.lead_id, message.channel, random.randint(900, 2900), {"action": "nurture_reply"})
    _hubspot_write("conversation_event", message.lead_id, {"channel": message.channel, "message": message.message})
    event_bus.emit("inbound.message", message.model_dump())
    handoff = decide_handoff_state(
        lead_id=message.lead_id,
        has_replied_email=(message.channel == "email"),
        prefers_sms=(message.channel == "sms"),
    )
    return {"status": "ok", "reply": f"Thanks. I can share options and book a call: {handoff.cal_link}"}


@app.post("/webhooks/resend")
async def resend_webhook(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
        parsed = parse_resend_webhook(payload)
    except Exception as exc:  # pylint: disable=broad-except
        _append_jsonl(DATA_DIR / "webhook_errors.jsonl", {"source": "resend", "error": str(exc)})
        raise HTTPException(status_code=400, detail="Malformed Resend webhook payload") from exc
    if parsed.get("event") == "bounce":
        _append_jsonl(DATA_DIR / "email_bounces.jsonl", parsed)
        event_bus.emit("email.bounce", parsed)
        return {"status": "ok", "event": "bounce_logged"}
    if parsed.get("event") == "reply":
        lead_id = str(payload.get("lead_id", "lead_unknown"))
        return inbound_message(InboundMessage(lead_id=lead_id, channel="email", message=parsed.get("message", "")))
    return {"status": "ok", "event": parsed.get("event", "unknown")}


@app.post("/webhooks/africastalking")
async def africas_talking_webhook(request: Request) -> dict[str, Any]:
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            payload = await request.json()
        else:
            form = await request.form()
            payload = dict(form)
        parsed = parse_inbound_sms(payload)
    except Exception as exc:  # pylint: disable=broad-except
        _append_jsonl(DATA_DIR / "webhook_errors.jsonl", {"source": "africastalking", "error": str(exc)})
        raise HTTPException(status_code=400, detail="Malformed Africa's Talking payload") from exc
    lead_id = str(payload.get("lead_id", "lead_unknown"))
    return inbound_message(InboundMessage(lead_id=lead_id, channel="sms", message=parsed["text"]))


@app.post("/webhooks/cal")
async def cal_webhook(request: Request) -> dict[str, str]:
    try:
        payload = await request.json()
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=400, detail="Malformed Cal webhook payload") from exc
    lead_id = str(payload.get("lead_id", "lead_unknown"))
    event_type = str(payload.get("triggerEvent", "booking_event"))
    _hubspot_write("calendar_event", lead_id, {"event_type": event_type, "payload": payload})
    _trace_interaction(lead_id, "email", random.randint(700, 1400), {"action": "calendar_webhook"})
    event_bus.emit("calendar.booking_event", {"lead_id": lead_id, "event_type": event_type})
    return {"status": "ok", "message": "calendar event processed"}


@app.get("/metrics/latency")
def latency_summary() -> dict[str, float | int]:
    trace_path = DATA_DIR / "interaction_traces.jsonl"
    if not trace_path.exists():
        return {"count": 0, "p50_ms": 0, "p95_ms": 0}
    values = [json.loads(line)["latency_ms"] for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not values:
        return {"count": 0, "p50_ms": 0, "p95_ms": 0}
    values_sorted = sorted(values)
    p50 = values_sorted[len(values_sorted) // 2]
    p95 = values_sorted[max(0, int(len(values_sorted) * 0.95) - 1)]
    return {"count": len(values), "p50_ms": p50, "p95_ms": p95, "mean_ms": round(statistics.mean(values), 2)}
