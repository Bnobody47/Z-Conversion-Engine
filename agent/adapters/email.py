from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class EmailMessage:
    to_email: str
    subject: str
    body: str


def send_email(message: EmailMessage) -> dict:
    raise NotImplementedError("Use send_email_with_provider()")


def send_email_with_provider(
    message: EmailMessage,
    *,
    provider: str,
    api_key: str,
    from_email: str,
    timeout_s: int = 20,
) -> dict[str, Any]:
    try:
        if provider == "resend":
            return _send_resend(message, api_key, from_email, timeout_s)
        if provider == "mailersend":
            return _send_mailersend(message, api_key, from_email, timeout_s)
        return {"ok": False, "error": f"unsupported_provider:{provider}"}
    except Exception as exc:  # pylint: disable=broad-except
        return {"ok": False, "error": f"email_send_failed:{exc}"}


def parse_resend_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    # Expected event values include email.sent, email.delivered, email.bounced, email.complained
    event_type = str(payload.get("type", "")).lower()
    data = payload.get("data", {}) if isinstance(payload.get("data"), dict) else {}
    to_email = data.get("to", [""])[0] if isinstance(data.get("to"), list) else data.get("to", "")
    subject = str(data.get("subject", ""))
    text = str(data.get("text", data.get("html", "")))
    if not event_type:
        raise ValueError("missing_event_type")
    if "bounced" in event_type:
        return {"event": "bounce", "to_email": to_email, "reason": str(data.get("bounce", "unknown"))}
    if "delivered" in event_type or "sent" in event_type:
        return {"event": "delivery_status", "to_email": to_email, "status": event_type}
    if "inbound" in event_type or "received" in event_type:
        return {"event": "reply", "to_email": to_email, "message": text, "subject": subject}
    return {"event": "unknown", "raw_type": event_type}


def _send_resend(message: EmailMessage, api_key: str, from_email: str, timeout_s: int) -> dict[str, Any]:
    url = "https://api.resend.com/emails"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "from": from_email,
        "to": [message.to_email],
        "subject": message.subject,
        "text": message.body,
        "headers": {"X-Tenacious-Status": "draft"},
    }
    with httpx.Client(timeout=timeout_s) as client:
        response = client.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        return {"ok": False, "provider": "resend", "error": f"http_{response.status_code}", "body": response.text}
    return {"ok": True, "provider": "resend", "message_id": response.json().get("id")}


def _send_mailersend(message: EmailMessage, api_key: str, from_email: str, timeout_s: int) -> dict[str, Any]:
    url = "https://api.mailersend.com/v1/email"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "from": {"email": from_email},
        "to": [{"email": message.to_email}],
        "subject": message.subject,
        "text": message.body,
        "headers": {"X-Tenacious-Status": "draft"},
    }
    with httpx.Client(timeout=timeout_s) as client:
        response = client.post(url, headers=headers, json=body)
    if response.status_code >= 400:
        return {"ok": False, "provider": "mailersend", "error": f"http_{response.status_code}", "body": response.text}
    return {"ok": True, "provider": "mailersend", "status_code": response.status_code}
