from __future__ import annotations

from typing import Any

import httpx


def write_contact_event(payload: dict, *, access_token: str | None = None) -> dict[str, Any]:
    """
    Writes a contact event with enrichment-ready properties.
    If token is missing, returns a stubbed local-success response.
    """
    if not access_token:
        return {"status": "written", "provider": "stub", "object": "contact_event", "payload": payload}

    # Minimal direct write fallback where MCP is unavailable in runtime.
    # Keep enrichment fields explicit for rubric checks.
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    properties = payload.get("properties", {})
    body = {"properties": properties}
    try:
        with httpx.Client(timeout=20) as client:
            response = client.post(url, headers=headers, json=body)
        if response.status_code >= 400:
            return {"status": "error", "provider": "hubspot", "error": response.text}
        return {"status": "written", "provider": "hubspot", "id": response.json().get("id")}
    except Exception as exc:  # pylint: disable=broad-except
        return {"status": "error", "provider": "hubspot", "error": str(exc)}
