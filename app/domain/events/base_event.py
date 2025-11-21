"""
Base Domain Event using package-events-bus library.

Base class for all domain events.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID, uuid4

from events_bus.core import BaseEvent


class BaseDomainEvent(BaseEvent):
    """
    Base class for domain events.

    Domain events represent important facts that have occurred in the domain.
    They are named in past tense.

    Inherits from events_bus.core.BaseEvent for integration with package-events-bus library.

    Event name follows the pattern:
    [company].[service].[version].[message_type].[resource_name].[event_command_name]

    Example: "testclean.api.1.event.company.created"
    """

    def __init__(
        self,
        event_name: str,
        event_id: str | None = None,
        occurred_on: datetime | None = None,
        **kwargs
    ):
        """
        Initialize domain event.

        Args:
            event_name: Fully qualified event name
            event_id: Unique event identifier (generated if not provided)
            occurred_on: When the event occurred (now if not provided)
            **kwargs: Additional event attributes
        """
        # Call parent BaseEvent constructor
        super().__init__(
            event_name=event_name,
            event_id=event_id or uuid4().hex,
            occurred_on=occurred_on or datetime.now(tz=timezone.utc)
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary for serialization.

        Returns:
            Dict[str, Any]: Event data as dictionary
        """
        return {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "occurred_on": self.occurred_on.isoformat(),
        }

    @classmethod
    def from_dict(cls, event_id: str, occurred_on: datetime, attributes: dict) -> "BaseDomainEvent":
        """
        Create event from dictionary (deserialization).

        Args:
            event_id: Event unique identifier
            occurred_on: When the event occurred
            attributes: Event-specific attributes

        Returns:
            BaseDomainEvent instance
        """
        # This should be overridden in subclasses for custom deserialization
        # Get event_name from attributes or use class default
        event_name = attributes.get("event_name", cls._get_default_event_name())
        return cls(event_name=event_name, event_id=event_id, occurred_on=occurred_on)

    @classmethod
    def _get_default_event_name(cls) -> str:
        """
        Get default event name for this class.

        Override in subclasses to provide specific event names.

        Returns:
            str: Default event name
        """
        return f"testclean.api.1.event.base.{cls.__name__.lower()}"
