"""
Company Mapper.

Maps between Company domain objects and DTOs.
"""

from app.domain.aggregates.company_aggregate import CompanyAggregate
from app.application.dtos.company_dto import CompanyDTO


class CompanyMapper:
    """
    Mapper for Company aggregate and DTOs.

    Handles conversion between domain layer and application layer.
    """

    @staticmethod
    def to_dto(aggregate: CompanyAggregate) -> CompanyDTO:
        """
        Convert Company aggregate to DTO.

        Args:
            aggregate: Company aggregate from domain

        Returns:
            CompanyDTO: DTO for application/presentation layer
        """
        return CompanyDTO(
            company_id=aggregate.company_id,
            company_name=aggregate.company_name,
            country_id=aggregate.country_id,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )

    @staticmethod
    def to_aggregate(dto: CompanyDTO) -> CompanyAggregate:
        """
        Convert DTO to Company aggregate.

        Args:
            dto: Company DTO

        Returns:
            CompanyAggregate: Domain aggregate
        """
        return CompanyAggregate(
            company_id=dto.company_id,
            company_name=dto.company_name,
            country_id=dto.country_id,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
