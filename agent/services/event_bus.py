from __future__ import annotations

from collections.abc import Callable
from typing import Any


EventHandler = Callable[[dict[str, Any]], None]
_SUBSCRIBERS: dict[str, list[EventHandler]] = {}


def subscribe(event_name: str, handler: EventHandler) -> None:
    _SUBSCRIBERS.setdefault(event_name, []).append(handler)


def emit(event_name: str, payload: dict[str, Any]) -> None:
    for handler in _SUBSCRIBERS.get(event_name, []):
        handler(payload)
