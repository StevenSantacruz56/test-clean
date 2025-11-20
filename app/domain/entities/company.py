"""
Company Entity.

Represents a company with unique identity and lifecycle.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID


class Company:
    """
    Company entity with identity and business logic.

    A company has a unique identifier and represents a business entity
    in the system with its basic information.
    """

    def __init__(
        self,
        company_id: Optional[UUID],
        company_name: str,
        country_id: UUID,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """
        Initialize a Company entity.

        Args:
            company_id: Unique identifier (None for new companies)
            company_name: Name of the company
            country_id: Country where company is registered
            created_at: Timestamp of creation
            updated_at: Timestamp of last update
        """
        self.company_id = company_id
        self._company_name = company_name
        self._country_id = country_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at

        self._validate()

    def _validate(self) -> None:
        """Validate entity invariants."""
        if not self._company_name or len(self._company_name.strip()) == 0:
            raise ValueError("Company name cannot be empty")

        if len(self._company_name) > 255:
            raise ValueError("Company name cannot exceed 255 characters")

    @property
    def company_name(self) -> str:
        """Get company name."""
        return self._company_name

    @property
    def country_id(self) -> UUID:
        """Get country ID."""
        return self._country_id

    def update_name(self, new_name: str) -> None:
        """
        Update company name.

        Args:
            new_name: New company name

        Raises:
            ValueError: If name is invalid
        """
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Company name cannot be empty")

        if len(new_name) > 255:
            raise ValueError("Company name cannot exceed 255 characters")

        self._company_name = new_name
        self.updated_at = datetime.utcnow()

    def update_country(self, new_country_id: UUID) -> None:
        """
        Update company country.

        Args:
            new_country_id: New country UUID

        Raises:
            ValueError: If country_id is invalid
        """
        if not new_country_id:
            raise ValueError("Country ID cannot be empty")

        self._country_id = new_country_id
        self.updated_at = datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        """Compare companies by identity."""
        if not isinstance(other, Company):
            return False
        return self.company_id == other.company_id

    def __hash__(self) -> int:
        """Hash company by identity."""
        return hash(self.company_id)

    def __repr__(self) -> str:
        """String representation."""
        return f"Company(id={self.company_id}, name={self._company_name})"
