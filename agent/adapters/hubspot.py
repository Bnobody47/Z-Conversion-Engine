from __future__ import annotations


def write_contact_event(payload: dict) -> dict:
    """
    Adapter boundary for HubSpot MCP/server API.
    """
    return {"status": "written", "provider": "stub", "object": "contact_event", "payload": payload}
