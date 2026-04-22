from __future__ import annotations


def send_sms(phone_number: str, message: str) -> dict:
    """
    Adapter boundary for Africa's Talking integration.
    """
    return {"status": "queued", "provider": "stub", "to": phone_number, "chars": len(message)}
