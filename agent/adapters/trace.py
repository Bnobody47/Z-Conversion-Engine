from __future__ import annotations


def emit_trace(trace_payload: dict) -> dict:
    """
    Adapter boundary for Langfuse / OpenTelemetry sink.
    """
    return {"status": "sent", "provider": "stub", "trace_id": trace_payload.get("trace_id", "n/a")}
