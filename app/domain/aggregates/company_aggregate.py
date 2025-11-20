"""
Company Aggregate.

Root aggregate for company with its related information.
"""

from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID, uuid4

from app.domain.entities.company import Company
from app.domain.entities.company_type import CompanyType
from app.domain.value_objects.company_detail_vo import CompanyDetailVO
from app.domain.events.company_created import CompanyCreated
from app.domain.events.company_updated import CompanyUpdated


class CompanyAggregate:
    """
    Company aggregate root.

    Maintains transactional consistency for company and its related data.
    """

    def __init__(
        self,
        company_id: Optional[UUID] = None,
        company_name: str = "",
        country_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        details: Optional[List[CompanyDetailVO]] = None,
        company_types: Optional[List[CompanyType]] = None,
    ):
        """
        Initialize Company aggregate.

        Args:
            company_id: Unique identifier (None for new companies)
            company_name: Name of the company
            country_id: Country where company is registered
            created_at: Timestamp of creation
            updated_at: Timestamp of last update
            details: List of company details
            company_types: List of company types
        """
        self._company = Company(
            company_id=company_id,
            company_name=company_name,
            country_id=country_id or UUID("00000000-0000-0000-0000-000000000000"),
            created_at=created_at,
            updated_at=updated_at,
        )
        self._details: List[CompanyDetailVO] = details or []
        self._company_types: List[CompanyType] = company_types or []
        self._events: List = []

    @classmethod
    def create(cls, company_name: str, country_id: UUID) -> "CompanyAggregate":
        """
        Factory method to create a new company.

        Args:
            company_name: Name of the company
            country_id: Country where company is registered

        Returns:
            CompanyAggregate: New company aggregate

        Raises:
            ValueError: If validation fails
        """
        if not company_name or len(company_name.strip()) == 0:
            raise ValueError("Company name is required")

        if not country_id:
            raise ValueError("Country ID is required")

        company_id = uuid4()
        now = datetime.utcnow()

        aggregate = cls(
            company_id=company_id,
            company_name=company_name,
            country_id=country_id,
            created_at=now,
            updated_at=now,
        )

        # Register domain event
        aggregate._events.append(
            CompanyCreated(
                company_id=company_id,
                company_name=company_name,
                country_id=country_id,
                occurred_at=now,
            )
        )

        return aggregate

    def update(self, company_name: Optional[str] = None, country_id: Optional[UUID] = None) -> None:
        """
        Update company information.

        Args:
            company_name: New company name (optional)
            country_id: New country ID (optional)

        Raises:
            ValueError: If validation fails
        """
        updated = False

        if company_name is not None and company_name != self._company.company_name:
            self._company.update_name(company_name)
            updated = True

        if country_id is not None and country_id != self._company.country_id:
            self._company.update_country(country_id)
            updated = True

        if updated:
            # Register domain event
            self._events.append(
                CompanyUpdated(
                    company_id=self._company.company_id,
                    company_name=self._company.company_name,
                    country_id=self._company.country_id,
                    occurred_at=datetime.utcnow(),
                )
            )

    @property
    def company_id(self) -> Optional[UUID]:
        """Get company ID."""
        return self._company.company_id

    @property
    def company_name(self) -> str:
        """Get company name."""
        return self._company.company_name

    @property
    def country_id(self) -> UUID:
        """Get country ID."""
        return self._company.country_id

    @property
    def created_at(self) -> Optional[datetime]:
        """Get creation timestamp."""
        return self._company.created_at

    @property
    def updated_at(self) -> Optional[datetime]:
        """Get update timestamp."""
        return self._company.updated_at

    @property
    def details(self) -> List[CompanyDetailVO]:
        """Get company details (read-only)."""
        return self._details.copy()

    @property
    def company_types(self) -> List[CompanyType]:
        """Get company types (read-only)."""
        return self._company_types.copy()

    def add_detail(self, detail: CompanyDetailVO) -> None:
        """
        Add a company detail.

        Args:
            detail: Company detail value object

        Raises:
            ValueError: If detail is invalid
        """
        if not detail:
            raise ValueError("Detail cannot be None")

        # Check for duplicate identity numbers
        for existing_detail in self._details:
            if existing_detail.identity_number == detail.identity_number:
                raise ValueError(f"Detail with identity number {detail.identity_number} already exists")

        self._details.append(detail)

    def remove_detail(self, identity_number: str) -> bool:
        """
        Remove a company detail by identity number.

        Args:
            identity_number: Identity number of detail to remove

        Returns:
            bool: True if removed, False if not found
        """
        for i, detail in enumerate(self._details):
            if detail.identity_number == identity_number:
                self._details.pop(i)
                return True
        return False

    def add_company_type(self, company_type: CompanyType) -> None:
        """
        Add a company type.

        Args:
            company_type: Company type entity

        Raises:
            ValueError: If type already exists
        """
        if not company_type:
            raise ValueError("Company type cannot be None")

        # Check for duplicates
        for existing_type in self._company_types:
            if existing_type.company_types_id == company_type.company_types_id:
                raise ValueError(f"Company type {company_type.type_name} already assigned")

        self._company_types.append(company_type)

    def remove_company_type(self, company_types_id: UUID) -> bool:
        """
        Remove a company type.

        Args:
            company_types_id: Company type ID to remove

        Returns:
            bool: True if removed, False if not found
        """
        for i, ctype in enumerate(self._company_types):
            if ctype.company_types_id == company_types_id:
                self._company_types.pop(i)
                return True
        return False

    @property
    def events(self) -> List:
        """Get domain events."""
        return self._events.copy()

    def clear_events(self) -> None:
        """Clear domain events after publishing."""
        self._events.clear()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CompanyAggregate(id={self.company_id}, name={self.company_name}, "
            f"details={len(self._details)}, types={len(self._company_types)})"
        )
