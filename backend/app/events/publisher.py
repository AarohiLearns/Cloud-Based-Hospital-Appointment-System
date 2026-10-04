"""Domain-event publishing.

Services only know the EventPublisher interface. Today events are just logged; later you can
add another implementation (message queue, email sender, ...) and select it in get_publisher()
without touching any business logic.
"""
import logging
from functools import lru_cache
from typing import Any, Protocol

logger = logging.getLogger(__name__)


class EventPublisher(Protocol):
    async def publish(self, event_type: str, payload: dict[str, Any]) -> None: ...


class LogPublisher:
    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        logger.info("event %s %s", event_type, payload)


@lru_cache
def get_publisher() -> EventPublisher:
    return LogPublisher()
