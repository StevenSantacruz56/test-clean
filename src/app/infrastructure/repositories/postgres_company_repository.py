"""
PostgreSQL Company Repository Implementation.

Concrete implementation of CompanyRepository using PostgreSQL.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.aggregates.company_aggregate import CompanyAggregate
from app.domain.repositories.company_repository import CompanyRepository
from app.infrastructure.database.postgres.models.company_model import CompanyModel


class PostgresCompanyRepository(CompanyRepository):
    """
    PostgreSQL implementation of CompanyRepository.

    Implements the repository interface using SQLAlchemy and PostgreSQL.
    Handles conversion between domain aggregates and ORM models.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def save(self, company: CompanyAggregate) -> CompanyAggregate:
        """
        Save a company (create or update).

        Args:
            company: Company aggregate to save

        Returns:
            CompanyAggregate: Saved company aggregate
        """
        # Convert aggregate to ORM model
        model = self._aggregate_to_model(company)

        # Use merge for upsert behavior
        merged_model = await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(merged_model)

        # Convert back to aggregate
        return self._model_to_aggregate(merged_model)

    async def find_by_id(self, company_id: UUID) -> Optional[CompanyAggregate]:
        """
        Find a company by its ID.

        Args:
            company_id: Company UUID

        Returns:
            Optional[CompanyAggregate]: Company if found, None otherwise
        """
        stmt = select(CompanyModel).where(CompanyModel.company_id == company_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_aggregate(model)

    async def find_by_name(self, company_name: str) -> Optional[CompanyAggregate]:
        """
        Find a company by its name.

        Args:
            company_name: Company name

        Returns:
            Optional[CompanyAggregate]: Company if found, None otherwise
        """
        stmt = select(CompanyModel).where(CompanyModel.company_name == company_name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_aggregate(model)

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[CompanyAggregate]:
        """
        Find all companies with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[CompanyAggregate]: List of companies
        """
        stmt = select(CompanyModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self._model_to_aggregate(model) for model in models]

    async def exists(self, company_id: UUID) -> bool:
        """
        Check if a company exists.

        Args:
            company_id: Company UUID

        Returns:
            bool: True if exists, False otherwise
        """
        stmt = select(CompanyModel.company_id).where(CompanyModel.company_id == company_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def delete(self, company_id: UUID) -> bool:
        """
        Delete a company.

        Args:
            company_id: Company UUID

        Returns:
            bool: True if deleted, False if not found
        """
        stmt = select(CompanyModel).where(CompanyModel.company_id == company_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self.session.delete(model)
        await self.session.flush()
        return True

    def _aggregate_to_model(self, aggregate: CompanyAggregate) -> CompanyModel:
        """
        Convert domain aggregate to ORM model.

        Args:
            aggregate: Company aggregate

        Returns:
            CompanyModel: ORM model
        """
        return CompanyModel(
            company_id=aggregate.company_id,
            company_name=aggregate.company_name,
            country_id=aggregate.country_id,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

    def _model_to_aggregate(self, model: CompanyModel) -> CompanyAggregate:
        """
        Convert ORM model to domain aggregate.

        Args:
            model: ORM model

        Returns:
            CompanyAggregate: Domain aggregate
        """
        return CompanyAggregate(
            company_id=model.company_id,
            company_name=model.company_name,
            country_id=model.country_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
