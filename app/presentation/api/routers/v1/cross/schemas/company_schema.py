"""
Company API Schemas.

Pydantic schemas for company API requests and responses.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator, EmailStr


class CompanyDetailSchema(BaseModel):
    """
    Schema for company detail information.
    """

    identification_type_id: UUID = Field(..., description="UUID of the identification type")
    identity_number: str = Field(..., description="Identity/Tax number", min_length=1, max_length=255)
    address: Optional[str] = Field(None, description="Company address", max_length=255)
    number_indicative: Optional[str] = Field(None, description="Phone country code", max_length=255)
    phone_number: Optional[str] = Field(None, description="Phone number", max_length=255)
    email: Optional[EmailStr] = Field(None, description="Contact email")
    city_id: Optional[UUID] = Field(None, description="UUID of the city")
    active: bool = Field(True, description="Is detail active")
    person_type: Optional[str] = Field(None, description="Person type", max_length=255)
    status: Optional[str] = Field(None, description="Status", max_length=255)
    verified: bool = Field(False, description="Is detail verified")

    class Config:
        schema_extra = {
            "example": {
                "identification_type_id": "123e4567-e89b-12d3-a456-426614174000",
                "identity_number": "123456789",
                "address": "123 Main St",
                "number_indicative": "+1",
                "phone_number": "5551234567",
                "email": "contact@techsolutions.com",
                "city_id": "123e4567-e89b-12d3-a456-426614174001",
                "active": True,
                "person_type": "Legal",
                "status": "Active",
                "verified": False,
            }
        }


class CompanyTypeSchema(BaseModel):
    """
    Schema for company type information.
    """

    company_types_id: UUID = Field(..., description="UUID of the company type")
    type_name: str = Field(..., description="Name of the company type")

    class Config:
        schema_extra = {
            "example": {"company_types_id": "123e4567-e89b-12d3-a456-426614174000", "type_name": "Retailer"}
        }


class CompanyCreateRequest(BaseModel):
    """
    Schema for creating a company.

    Request body for POST /api/v1/companies
    """

    company_name: str = Field(
        ...,
        description="Name of the company",
        min_length=1,
        max_length=255,
        example="Tech Solutions Inc.",
    )
    country_id: UUID = Field(
        ...,
        description="UUID of the country where the company is registered",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    details: Optional[List[CompanyDetailSchema]] = Field(
        None, description="List of company details (identification, contact info)"
    )
    company_type_ids: Optional[List[UUID]] = Field(None, description="List of company type UUIDs to assign")

    @validator("company_name")
    def validate_company_name(cls, v: str) -> str:
        """Validate company name is not empty after stripping."""
        if not v or not v.strip():
            raise ValueError("Company name cannot be empty or whitespace")
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "company_name": "Tech Solutions Inc.",
                "country_id": "123e4567-e89b-12d3-a456-426614174000",
                "details": [
                    {
                        "identification_type_id": "123e4567-e89b-12d3-a456-426614174002",
                        "identity_number": "123456789",
                        "email": "contact@techsolutions.com",
                        "phone_number": "5551234567",
                        "active": True,
                    }
                ],
                "company_type_ids": ["123e4567-e89b-12d3-a456-426614174003"],
            }
        }


class CompanyUpdateRequest(BaseModel):
    """
    Schema for updating a company.

    Request body for PUT /api/v1/companies/{company_id}
    All fields are optional for partial updates.
    """

    company_name: Optional[str] = Field(
        None,
        description="New name of the company",
        min_length=1,
        max_length=255,
        example="Tech Solutions Corp.",
    )
    country_id: Optional[UUID] = Field(
        None,
        description="New UUID of the country",
        example="123e4567-e89b-12d3-a456-426614174001",
    )
    details: Optional[List[CompanyDetailSchema]] = Field(
        None, description="Updated list of company details (replaces existing)"
    )
    company_type_ids: Optional[List[UUID]] = Field(
        None, description="Updated list of company type UUIDs (replaces existing)"
    )

    @validator("company_name")
    def validate_company_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate company name if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Company name cannot be empty or whitespace")
            return v.strip()
        return v

    class Config:
        schema_extra = {
            "example": {
                "company_name": "Tech Solutions Corp.",
                "country_id": "123e4567-e89b-12d3-a456-426614174001",
                "details": [
                    {
                        "identification_type_id": "123e4567-e89b-12d3-a456-426614174002",
                        "identity_number": "987654321",
                        "email": "info@techsolutions.com",
                    }
                ],
                "company_type_ids": ["123e4567-e89b-12d3-a456-426614174003"],
            }
        }


class CompanyResponse(BaseModel):
    """
    Schema for company response.

    Response body for company endpoints.
    """

    company_id: UUID = Field(..., description="Unique identifier of the company")
    company_name: str = Field(..., description="Name of the company")
    country_id: UUID = Field(..., description="UUID of the country")
    created_at: datetime = Field(..., description="Timestamp when company was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when company was last updated")
    details: Optional[List[CompanyDetailSchema]] = Field(None, description="List of company details")
    company_types: Optional[List[CompanyTypeSchema]] = Field(None, description="List of assigned company types")

    class Config:
        schema_extra = {
            "example": {
                "company_id": "123e4567-e89b-12d3-a456-426614174000",
                "company_name": "Tech Solutions Inc.",
                "country_id": "123e4567-e89b-12d3-a456-426614174001",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-02T12:00:00Z",
                "details": [
                    {
                        "identification_type_id": "123e4567-e89b-12d3-a456-426614174002",
                        "identity_number": "123456789",
                        "email": "contact@techsolutions.com",
                        "active": True,
                        "verified": False,
                    }
                ],
                "company_types": [
                    {"company_types_id": "123e4567-e89b-12d3-a456-426614174003", "type_name": "Retailer"}
                ],
            }
        }


class ErrorResponse(BaseModel):
    """
    Schema for error responses.

    Standard error response format.
    """

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")

    class Config:
        schema_extra = {
            "example": {
                "detail": "Company not found",
                "error_code": "COMPANY_NOT_FOUND",
            }
        }
