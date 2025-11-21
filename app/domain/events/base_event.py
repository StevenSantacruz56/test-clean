"""
Base Domain Event using package-events-bus library.

Base class for all domain events.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4

from events_bus.core import BaseEvent


@dataclass
class BaseDomainEvent(BaseEvent):
    """
    Base class for domain events.

    Domain events represent important facts that have occurred in the domain.
    They are named in past tense.

    Inherits from events_bus.core.BaseEvent for integration with package-events-bus library.
    """

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.utcnow())

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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseDomainEvent":
        """
        Create event from dictionary.

        Args:
            data: Dictionary with event data

        Returns:
            BaseDomainEvent instance
        """
        # This can be overridden in subclasses for custom deserialization
        return cls()
