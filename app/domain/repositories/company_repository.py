"""
Company Repository Interface.

Abstract interface for company persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.aggregates.company_aggregate import CompanyAggregate


class CompanyRepository(ABC):
    """
    Repository interface for Company aggregate.

    This is an abstraction that defines WHAT operations are needed,
    not HOW they are implemented. Infrastructure layer provides concrete implementation.
    """

    @abstractmethod
    async def save(self, company: CompanyAggregate) -> CompanyAggregate:
        """
        Save a company (create or update).

        Args:
            company: Company aggregate to save

        Returns:
            CompanyAggregate: Saved company aggregate

        Raises:
            RepositoryException: If save operation fails
        """
        pass

    @abstractmethod
    async def find_by_id(self, company_id: UUID) -> Optional[CompanyAggregate]:
        """
        Find a company by its ID.

        Args:
            company_id: Company UUID

        Returns:
            Optional[CompanyAggregate]: Company if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_name(self, company_name: str) -> Optional[CompanyAggregate]:
        """
        Find a company by its name.

        Args:
            company_name: Company name

        Returns:
            Optional[CompanyAggregate]: Company if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[CompanyAggregate]:
        """
        Find all companies with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[CompanyAggregate]: List of companies
        """
        pass

    @abstractmethod
    async def exists(self, company_id: UUID) -> bool:
        """
        Check if a company exists.

        Args:
            company_id: Company UUID

        Returns:
            bool: True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def delete(self, company_id: UUID) -> bool:
        """
        Delete a company.

        Args:
            company_id: Company UUID

        Returns:
            bool: True if deleted, False if not found
        """
        pass
