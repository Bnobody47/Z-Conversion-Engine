from __future__ import annotations


def create_booking(payload: dict) -> dict:
    """
    Adapter boundary for Cal.com booking flow.
    """
    return {"status": "booked", "provider": "stub", "booking": payload}
