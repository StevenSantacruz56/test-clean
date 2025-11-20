"""
Get Company Use Case.

Use case for retrieving a company by ID.
"""

from uuid import UUID

from app.domain.repositories.company_repository import CompanyRepository
from app.domain.exceptions.company_exceptions import CompanyNotFoundException
from app.application.dtos.company_dto import CompanyDTO
from app.application.mappers.company_mapper import CompanyMapper


class GetCompanyUseCase:
    """
    Use Case: Get a company by ID.

    This use case retrieves a single company by its unique identifier.
    """

    def __init__(self, company_repository: CompanyRepository):
        """
        Initialize use case.

        Args:
            company_repository: Repository for company retrieval
        """
        self.company_repository = company_repository

    async def execute(self, company_id: UUID) -> CompanyDTO:
        """
        Execute the get company use case.

        Args:
            company_id: ID of the company to retrieve

        Returns:
            CompanyDTO: Company data

        Raises:
            CompanyNotFoundException: If company doesn't exist
        """
        # Find company
        company_aggregate = await self.company_repository.find_by_id(company_id)
        if not company_aggregate:
            raise CompanyNotFoundException(company_id)

        # Convert to DTO and return
        return CompanyMapper.to_dto(company_aggregate)
