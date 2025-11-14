"""
Company DTOs (Data Transfer Objects).

DTOs for transferring company data between layers.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID


@dataclass
class CompanyDetailDTO:
    """
    DTO for company detail information.
    """

    identification_type_id: UUID
    identity_number: str
    address: Optional[str] = None
    number_indicative: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    city_id: Optional[UUID] = None
    active: bool = True
    person_type: Optional[str] = None
    status: Optional[str] = None
    verified: bool = False


@dataclass
class CompanyTypeDTO:
    """
    DTO for company type information.
    """

    company_types_id: UUID
    type_name: str


@dataclass
class CreateCompanyDTO:
    """
    DTO for creating a company.

    This DTO carries the data needed to create a new company.
    """

    company_name: str
    country_id: UUID
    details: Optional[List[CompanyDetailDTO]] = None
    company_type_ids: Optional[List[UUID]] = None


@dataclass
class UpdateCompanyDTO:
    """
    DTO for updating a company.

    This DTO carries the data for updating an existing company.
    All fields are optional to support partial updates.
    """

    company_name: Optional[str] = None
    country_id: Optional[UUID] = None
    details: Optional[List[CompanyDetailDTO]] = None
    company_type_ids: Optional[List[UUID]] = None


@dataclass
class CompanyDTO:
    """
    DTO for company response.

    This DTO represents a company for API responses.
    """

    company_id: UUID
    company_name: str
    country_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    details: Optional[List[CompanyDetailDTO]] = None
    company_types: Optional[List[CompanyTypeDTO]] = None
