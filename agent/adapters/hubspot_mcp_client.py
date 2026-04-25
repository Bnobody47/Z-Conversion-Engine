from __future__ import annotations

from typing import Any

from agent.adapters.hubspot import write_contact_event


def create_or_update_contact(properties: dict[str, Any], access_token: str | None) -> dict[str, Any]:
    """
    MCP-facing wrapper for contact creation/update events.
    """
    return write_contact_event({"properties": properties}, access_token=access_token)


def log_activity(activity_payload: dict[str, Any], access_token: str | None) -> dict[str, Any]:
    """
    MCP-facing wrapper for activity/event logging.
    """
    return write_contact_event({"properties": activity_payload}, access_token=access_token)


def write_enrichment_fields(enrichment_payload: dict[str, Any], access_token: str | None) -> dict[str, Any]:
    """
    MCP-facing wrapper for enrichment field writes.
    """
    return write_contact_event({"properties": enrichment_payload}, access_token=access_token)
