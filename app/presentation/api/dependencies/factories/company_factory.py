"""
Company Use Case Factory.

Factory for creating company use cases with dependency injection.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.company.create_company import CreateCompanyUseCase
from app.application.use_cases.company.update_company import UpdateCompanyUseCase
from app.application.use_cases.company.get_company import GetCompanyUseCase
from app.application.services.event_bus import get_event_bus, EventBusService
from app.infrastructure.repositories.postgres_company_repository import PostgresCompanyRepository
from app.presentation.api.dependencies.database import get_db


class CompanyFactory:
    """
    Factory for creating company use cases.

    Centralizes dependency injection for company-related use cases.
    """

    @staticmethod
    def create_company_use_case(
        db: AsyncSession = Depends(get_db),
        event_bus: EventBusService = Depends(get_event_bus),
    ) -> CreateCompanyUseCase:
        """
        Create the CreateCompanyUseCase with all dependencies.

        Args:
            db: Database session
            event_bus: Event bus for publishing domain events

        Returns:
            CreateCompanyUseCase: Configured use case
        """
        company_repository = PostgresCompanyRepository(db)
        return CreateCompanyUseCase(
            company_repository=company_repository,
            event_bus=event_bus
        )

    @staticmethod
    def update_company_use_case(
        db: AsyncSession = Depends(get_db),
        event_bus: EventBusService = Depends(get_event_bus),
    ) -> UpdateCompanyUseCase:
        """
        Create the UpdateCompanyUseCase with all dependencies.

        Args:
            db: Database session
            event_bus: Event bus for publishing domain events

        Returns:
            UpdateCompanyUseCase: Configured use case
        """
        company_repository = PostgresCompanyRepository(db)
        return UpdateCompanyUseCase(
            company_repository=company_repository,
            event_bus=event_bus
        )

    @staticmethod
    def get_company_use_case(
        db: AsyncSession = Depends(get_db),
    ) -> GetCompanyUseCase:
        """
        Create the GetCompanyUseCase with all dependencies.

        Args:
            db: Database session

        Returns:
            GetCompanyUseCase: Configured use case
        """
        company_repository = PostgresCompanyRepository(db)
        return GetCompanyUseCase(company_repository=company_repository)
