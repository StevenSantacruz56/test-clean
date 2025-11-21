"""
Update Company Use Case.

Use case for updating an existing company.
"""

from uuid import UUID

from app.domain.aggregates.company_aggregate import CompanyAggregate
from app.domain.repositories.company_repository import CompanyRepository
from app.domain.exceptions.company_exceptions import CompanyNotFoundException, CompanyAlreadyExistsException
from app.application.dtos.company_dto import UpdateCompanyDTO, CompanyDTO
from app.application.mappers.company_mapper import CompanyMapper
from app.application.services.event_bus import EventBusService


class UpdateCompanyUseCase:
    """
    Use Case: Update an existing company.

    This use case handles updating company information.
    It validates business rules, updates the aggregate, and persists changes.
    """

    def __init__(
        self,
        company_repository: CompanyRepository,
        event_bus: EventBusService
    ):
        """
        Initialize use case.

        Args:
            company_repository: Repository for company persistence
            event_bus: Event bus for publishing domain events
        """
        self.company_repository = company_repository
        self.event_bus = event_bus

    async def execute(self, company_id: UUID, dto: UpdateCompanyDTO) -> CompanyDTO:
        """
        Execute the update company use case.

        Args:
            company_id: ID of the company to update
            dto: Data for updating the company

        Returns:
            CompanyDTO: Updated company data

        Raises:
            CompanyNotFoundException: If company doesn't exist
            CompanyAlreadyExistsException: If new name conflicts with existing company
            ValueError: If validation fails
        """
        # Find existing company
        company_aggregate = await self.company_repository.find_by_id(company_id)
        if not company_aggregate:
            raise CompanyNotFoundException(company_id)

        # If updating name, check if new name already exists
        if dto.company_name and dto.company_name != company_aggregate.company_name:
            existing_company = await self.company_repository.find_by_name(dto.company_name)
            if existing_company and existing_company.company_id != company_id:
                raise CompanyAlreadyExistsException(dto.company_name)

        # Update the aggregate (domain logic)
        company_aggregate.update(
            company_name=dto.company_name,
            country_id=dto.country_id,
        )

        # Persist the updated aggregate
        saved_company = await self.company_repository.save(company_aggregate)

        # Publish domain events
        for event in saved_company.events:
            await self.event_bus.publish(event)
        saved_company.clear_events()

        # Convert to DTO and return
        return CompanyMapper.to_dto(saved_company)
