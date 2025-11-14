"""
Company Detail Value Object.

Immutable value object representing company detail information.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class CompanyDetailVO:
    """
    Value Object for company detail information.

    Immutable representation of company identification and contact details.
    """

    identification_type_id: UUID
    identity_number: str
    address: Optional[str] = None
    number_indicative: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    city_id: Optional[UUID] = None
    active: bool = True
    person_type: Optional[str] = None
    status: Optional[str] = None
    verified: bool = False

    def __post_init__(self):
        """Validate value object invariants."""
        if not self.identification_type_id:
            raise ValueError("Identification type ID is required")

        if not self.identity_number or not self.identity_number.strip():
            raise ValueError("Identity number is required")

        if self.email and not self._is_valid_email(self.email):
            raise ValueError(f"Invalid email format: {self.email}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Basic email validation."""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        """String representation."""
        return f"CompanyDetail(identity={self.identity_number}, email={self.email})"
