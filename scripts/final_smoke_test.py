from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx


BASE_URL = "http://127.0.0.1:8010"
OUTPUT_PATH = Path("docs/final_smoke_test_output.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run() -> dict:
    out: dict[str, object] = {"started_at": utc_now(), "base_url": BASE_URL}
    with httpx.Client(timeout=30) as client:
        out["health"] = _response(client.get(f"{BASE_URL}/health"))

        lead_payload = {
            "company_name": "Submission Demo Co",
            "website": "submission-demo.co",
            "email": "submission-demo@example.com",
            "phone": "+251911555555",
            "synthetic": True,
        }
        lead_resp = client.post(f"{BASE_URL}/leads/process", json=lead_payload)
        out["leads_process"] = _response(lead_resp)
        lead_id = lead_resp.json().get("lead_id", "lead_unknown")

        out["outbound_email"] = _response(
            client.post(
                f"{BASE_URL}/outbound/email",
                json={
                    "lead_id": lead_id,
                    "to_email": "qa-receiver@example.com",
                    "subject": "Request: Discovery call",
                    "body": "Can we do 15 minutes this week?",
                },
            )
        )

        out["outbound_sms_before_reply"] = _response(
            client.post(
                f"{BASE_URL}/outbound/sms",
                json={"lead_id": lead_id, "to_phone": "+251911000000", "message": "Warm follow-up"},
            )
        )

        out["inbound_email_reply"] = _response(
            client.post(
                f"{BASE_URL}/webhooks/inbound",
                json={"lead_id": lead_id, "channel": "email", "message": "Yes, interested."},
            )
        )

        out["outbound_sms_after_reply"] = _response(
            client.post(
                f"{BASE_URL}/outbound/sms",
                json={"lead_id": lead_id, "to_phone": "+251911000000", "message": "Warm follow-up"},
            )
        )

        out["resend_bounce_webhook"] = _response(
            client.post(
                f"{BASE_URL}/webhooks/resend",
                json={"type": "email.bounced", "data": {"to": ["qa-receiver@example.com"], "bounce": "hard_bounce"}},
            )
        )

        out["cal_webhook"] = _response(
            client.post(
                f"{BASE_URL}/webhooks/cal",
                json={"lead_id": lead_id, "triggerEvent": "BOOKING_CREATED", "bookingId": "bk_final_demo"},
            )
        )

        out["latency"] = _response(client.get(f"{BASE_URL}/metrics/latency"))
        out["hubspot_check"] = _response(
            client.get("https://api.hubapi.com/crm/v3/objects/contacts?limit=1", headers=_hubspot_auth_header())
        )

    out["completed_at"] = utc_now()
    out["pass_summary"] = {
        "api_health_ok": out["health"]["status_code"] == 200,
        "lead_created": out["leads_process"]["status_code"] == 200,
        "sms_gate_before_reply": out["outbound_sms_before_reply"]["status_code"] == 400,
        "sms_allowed_after_reply": out["outbound_sms_after_reply"]["status_code"] == 200,
        "hubspot_reachable": out["hubspot_check"]["status_code"] == 200,
    }
    return out


def _hubspot_auth_header() -> dict[str, str]:
    env_lines = Path(".env").read_text(encoding="utf-8").splitlines()
    token = ""
    for line in env_lines:
        if line.startswith("HUBSPOT_ACCESS_TOKEN="):
            token = line.split("=", 1)[1].strip().strip('"')
            break
    return {"Authorization": f"Bearer {token}"} if token else {}


def _response(resp: httpx.Response) -> dict[str, object]:
    body = resp.text
    parsed: object
    try:
        parsed = resp.json()
    except Exception:
        parsed = body[:400]
    return {"status_code": resp.status_code, "body": parsed}


if __name__ == "__main__":
    result = run()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output_path": str(OUTPUT_PATH), "pass_summary": result["pass_summary"]}, indent=2))
