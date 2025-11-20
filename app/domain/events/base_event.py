"""
Base Domain Event.

Base class for all domain events using package-events-bus.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from package_events_bus import Event


@dataclass
class BaseDomainEvent(Event):
    """
    Base class for domain events.

    Domain events represent important facts that have occurred in the domain.
    They are named in past tense.

    Inherits from package_events_bus.Event for event bus integration.
    """

    event_id: UUID
    occurred_at: datetime

    def __init__(self, occurred_at: Optional[datetime] = None):
        """
        Initialize base domain event.

        Args:
            occurred_at: When the event occurred (defaults to now)
        """
        self.event_id = uuid4()
        self.occurred_at = occurred_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary.

        Returns:
            Dict[str, Any]: Event data as dictionary
        """
        return {
            "event_id": str(self.event_id),
            "event_type": self.__class__.__name__,
            "occurred_at": self.occurred_at.isoformat(),
        }
