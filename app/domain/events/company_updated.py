"""
Company Updated Event.

Event triggered when a company is updated.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from app.domain.events.base_event import BaseDomainEvent


@dataclass
class CompanyUpdated(BaseDomainEvent):
    """
    Event: Company was updated.

    This event is triggered when company information is updated.
    """

    company_id: UUID
    company_name: str
    country_id: UUID

    def __init__(
        self,
        company_id: UUID,
        company_name: str,
        country_id: UUID,
        occurred_at: Optional[datetime] = None,
    ):
        """
        Initialize CompanyUpdated event.

        Args:
            company_id: ID of the updated company
            company_name: Updated name
            country_id: Updated country ID
            occurred_at: When the event occurred
        """
        super().__init__(occurred_at)
        self.company_id = company_id
        self.company_name = company_name
        self.country_id = country_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        data = super().to_dict()
        data.update(
            {
                "company_id": str(self.company_id),
                "company_name": self.company_name,
                "country_id": str(self.country_id),
            }
        )
        return data
