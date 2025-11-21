"""
Base Domain Event.

Base class for all domain events.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


@dataclass
class BaseDomainEvent:
    """
    Base class for domain events.

    Domain events represent important facts that have occurred in the domain.
    They are named in past tense.
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
