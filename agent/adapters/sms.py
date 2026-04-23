from __future__ import annotations

from typing import Any

import httpx


def send_sms(
    phone_number: str,
    message: str,
    *,
    username: str,
    api_key: str,
    timeout_s: int = 20,
) -> dict[str, Any]:
    url = "https://api.africastalking.com/version1/messaging"
    headers = {"apiKey": api_key, "Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"username": username, "to": phone_number, "message": message}
    try:
        with httpx.Client(timeout=timeout_s) as client:
            response = client.post(url, headers=headers, data=data)
        if response.status_code >= 400:
            return {"ok": False, "provider": "africastalking", "error": f"http_{response.status_code}", "body": response.text}
        return {"ok": True, "provider": "africastalking", "response": response.json()}
    except Exception as exc:  # pylint: disable=broad-except
        return {"ok": False, "provider": "africastalking", "error": f"sms_send_failed:{exc}"}


def parse_inbound_sms(payload: dict[str, Any]) -> dict[str, str]:
    """
    Supports typical Africa's Talking callback fields such as text/message/from.
    """
    text = str(payload.get("text") or payload.get("message") or "").strip()
    sender = str(payload.get("from") or payload.get("phoneNumber") or "")
    if not text:
        raise ValueError("missing_sms_text")
    return {"text": text, "from": sender}
