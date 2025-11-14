"""
Company Endpoints (Cross-country).

API endpoints for company management.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.company.create_company import CreateCompanyUseCase
from app.application.use_cases.company.update_company import UpdateCompanyUseCase
from app.application.use_cases.company.get_company import GetCompanyUseCase
from app.application.dtos.company_dto import CreateCompanyDTO, UpdateCompanyDTO
from app.domain.exceptions.company_exceptions import (
    CompanyNotFoundException,
    CompanyAlreadyExistsException,
    InvalidCompanyException,
)
from app.presentation.api.dependencies.factories.company_factory import CompanyFactory
from app.presentation.api.routers.v1.cross.schemas.company_schema import (
    CompanyCreateRequest,
    CompanyUpdateRequest,
    CompanyResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CompanyResponse,
    summary="Create a new company",
    description="Create a new company in the system",
    responses={
        201: {"description": "Company created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid company data"},
        409: {"model": ErrorResponse, "description": "Company already exists"},
    },
)
async def create_company(
    request: CompanyCreateRequest,
    use_case: CreateCompanyUseCase = Depends(CompanyFactory.create_company_use_case),
) -> CompanyResponse:
    """
    Create a new company.

    This endpoint creates a new company with the provided information.

    Args:
        request: Company creation data
        use_case: Injected create company use case

    Returns:
        CompanyResponse: Created company data

    Raises:
        HTTPException: If validation fails or company already exists
    """
    try:
        # Convert request to DTO
        dto = CreateCompanyDTO(
            company_name=request.company_name,
            country_id=request.country_id,
        )

        # Execute use case
        result = await use_case.execute(dto)

        # Convert DTO to response
        return CompanyResponse(
            company_id=result.company_id,
            company_name=result.company_name,
            country_id=result.country_id,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    except CompanyAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with name '{e.company_name}' already exists",
        )
    except (ValueError, InvalidCompanyException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the company: {str(e)}",
        )


@router.put(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Update a company",
    description="Update an existing company's information",
    responses={
        200: {"description": "Company updated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid company data"},
        404: {"model": ErrorResponse, "description": "Company not found"},
        409: {"model": ErrorResponse, "description": "Company name already exists"},
    },
)
async def update_company(
    company_id: UUID,
    request: CompanyUpdateRequest,
    use_case: UpdateCompanyUseCase = Depends(CompanyFactory.update_company_use_case),
) -> CompanyResponse:
    """
    Update an existing company.

    This endpoint updates company information. All fields are optional.

    Args:
        company_id: UUID of the company to update
        request: Company update data
        use_case: Injected update company use case

    Returns:
        CompanyResponse: Updated company data

    Raises:
        HTTPException: If company not found or validation fails
    """
    try:
        # Convert request to DTO
        dto = UpdateCompanyDTO(
            company_name=request.company_name,
            country_id=request.country_id,
        )

        # Execute use case
        result = await use_case.execute(company_id, dto)

        # Convert DTO to response
        return CompanyResponse(
            company_id=result.company_id,
            company_name=result.company_name,
            country_id=result.country_id,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    except CompanyNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found",
        )
    except CompanyAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with name '{e.company_name}' already exists",
        )
    except (ValueError, InvalidCompanyException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the company: {str(e)}",
        )


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Get a company by ID",
    description="Retrieve a company by its unique identifier",
    responses={
        200: {"description": "Company found"},
        404: {"model": ErrorResponse, "description": "Company not found"},
    },
)
async def get_company(
    company_id: UUID,
    use_case: GetCompanyUseCase = Depends(CompanyFactory.get_company_use_case),
) -> CompanyResponse:
    """
    Get a company by ID.

    This endpoint retrieves a single company by its UUID.

    Args:
        company_id: UUID of the company to retrieve
        use_case: Injected get company use case

    Returns:
        CompanyResponse: Company data

    Raises:
        HTTPException: If company not found
    """
    try:
        # Execute use case
        result = await use_case.execute(company_id)

        # Convert DTO to response
        return CompanyResponse(
            company_id=result.company_id,
            company_name=result.company_name,
            country_id=result.country_id,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    except CompanyNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the company: {str(e)}",
        )
