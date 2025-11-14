"""
Company Type Entity.

Represents a type/category that can be assigned to companies.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID


class CompanyType:
    """
    Company Type entity.

    Represents a classification or category for companies
    (e.g., "Retailer", "Manufacturer", "Service Provider").
    """

    def __init__(
        self,
        company_types_id: Optional[UUID],
        type_name: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        """
        Initialize CompanyType entity.

        Args:
            company_types_id: Unique identifier
            type_name: Name of the company type
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.company_types_id = company_types_id
        self._type_name = type_name
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at

        self._validate()

    def _validate(self) -> None:
        """Validate entity invariants."""
        if not self._type_name or len(self._type_name.strip()) == 0:
            raise ValueError("Type name cannot be empty")

        if len(self._type_name) > 255:
            raise ValueError("Type name cannot exceed 255 characters")

    @property
    def type_name(self) -> str:
        """Get type name."""
        return self._type_name

    def update_name(self, new_name: str) -> None:
        """
        Update type name.

        Args:
            new_name: New type name

        Raises:
            ValueError: If name is invalid
        """
        if not new_name or len(new_name.strip()) == 0:
            raise ValueError("Type name cannot be empty")

        if len(new_name) > 255:
            raise ValueError("Type name cannot exceed 255 characters")

        self._type_name = new_name
        self.updated_at = datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        """Compare by identity."""
        if not isinstance(other, CompanyType):
            return False
        return self.company_types_id == other.company_types_id

    def __hash__(self) -> int:
        """Hash by identity."""
        return hash(self.company_types_id)

    def __repr__(self) -> str:
        """String representation."""
        return f"CompanyType(id={self.company_types_id}, name={self._type_name})"
