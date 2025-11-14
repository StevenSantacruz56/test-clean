"""
Create Company Use Case.

Use case for creating a new company.
"""

from app.domain.aggregates.company_aggregate import CompanyAggregate
from app.domain.repositories.company_repository import CompanyRepository
from app.domain.exceptions.company_exceptions import CompanyAlreadyExistsException
from app.application.dtos.company_dto import CreateCompanyDTO, CompanyDTO
from app.application.mappers.company_mapper import CompanyMapper


class CreateCompanyUseCase:
    """
    Use Case: Create a new company.

    This use case handles the creation of a new company in the system.
    It validates business rules, creates the aggregate, and persists it.
    """

    def __init__(self, company_repository: CompanyRepository):
        """
        Initialize use case.

        Args:
            company_repository: Repository for company persistence
        """
        self.company_repository = company_repository

    async def execute(self, dto: CreateCompanyDTO) -> CompanyDTO:
        """
        Execute the create company use case.

        Args:
            dto: Data for creating the company

        Returns:
            CompanyDTO: Created company data

        Raises:
            CompanyAlreadyExistsException: If company with same name exists
            ValueError: If validation fails
        """
        # Check if company with same name already exists
        existing_company = await self.company_repository.find_by_name(dto.company_name)
        if existing_company:
            raise CompanyAlreadyExistsException(dto.company_name)

        # Create company aggregate (domain logic)
        company_aggregate = CompanyAggregate.create(
            company_name=dto.company_name,
            country_id=dto.country_id,
        )

        # Persist the aggregate
        saved_company = await self.company_repository.save(company_aggregate)

        # TODO: Publish domain events
        # for event in saved_company.events:
        #     await self.event_bus.publish(event)
        # saved_company.clear_events()

        # Convert to DTO and return
        return CompanyMapper.to_dto(saved_company)
