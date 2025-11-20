"""
Domain Events.

Represent important facts or state changes in the domain.
Named in past tense (UserCreated, OrderPlaced, etc.).
"""

from app.domain.events.base_event import BaseDomainEvent
from app.domain.events.company_created import CompanyCreated
from app.domain.events.company_updated import CompanyUpdated

__all__ = [
    "BaseDomainEvent",
    "CompanyCreated",
    "CompanyUpdated",
]
