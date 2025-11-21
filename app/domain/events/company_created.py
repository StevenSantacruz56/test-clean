"""
Company Created Event.

Event triggered when a new company is created.
"""

from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from app.domain.events.base_event import BaseDomainEvent


class CompanyCreated(BaseDomainEvent):
    """
    Event: Company was created.

    This event is triggered when a new company is successfully created.

    Event name: testclean.api.1.event.company.created
    """

    EVENT_NAME = "testclean.api.1.event.company.created"

    def __init__(
        self,
        company_id: UUID,
        company_name: str,
        country_id: UUID,
        event_id: str | None = None,
        occurred_at: datetime | None = None
    ):
        """
        Initialize CompanyCreated event.

        Args:
            company_id: UUID of the created company
            company_name: Name of the created company
            country_id: UUID of the country
            event_id: Unique event identifier (optional)
            occurred_at: When the event occurred (optional)
        """
        super().__init__(
            event_name=self.EVENT_NAME,
            event_id=event_id,
            occurred_on=occurred_at
        )
        self.company_id = company_id
        self.company_name = company_name
        self.country_id = country_id

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary for serialization.

        Returns:
            Dict with all event data
        """
        data = super().to_dict()
        data.update(
            {
                "company_id": str(self.company_id),
                "company_name": self.company_name,
                "country_id": str(self.country_id),
            }
        )
        return data

    @classmethod
    def from_dict(cls, event_id: str, occurred_on: datetime, attributes: dict) -> "CompanyCreated":
        """
        Create event from dictionary (deserialization).

        Args:
            event_id: Event unique identifier
            occurred_on: When the event occurred
            attributes: Event attributes with company_id, company_name, country_id

        Returns:
            CompanyCreated event instance
        """
        return cls(
            company_id=UUID(attributes["company_id"]),
            company_name=attributes["company_name"],
            country_id=UUID(attributes["country_id"]),
            event_id=event_id,
            occurred_at=occurred_on
        )

    @classmethod
    def _get_default_event_name(cls) -> str:
        """Get default event name for this class."""
        return cls.EVENT_NAME
