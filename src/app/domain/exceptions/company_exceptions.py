"""
Company Domain Exceptions.

Exceptions specific to company business logic.
"""

from uuid import UUID

from app.domain.exceptions.domain_exception import DomainException


class CompanyNotFoundException(DomainException):
    """Exception raised when a company is not found."""

    def __init__(self, company_id: UUID):
        """
        Initialize exception.

        Args:
            company_id: ID of the company that was not found
        """
        super().__init__(f"Company with ID {company_id} not found")
        self.company_id = company_id


class CompanyAlreadyExistsException(DomainException):
    """Exception raised when trying to create a company that already exists."""

    def __init__(self, company_name: str):
        """
        Initialize exception.

        Args:
            company_name: Name of the company that already exists
        """
        super().__init__(f"Company with name '{company_name}' already exists")
        self.company_name = company_name


class InvalidCompanyException(DomainException):
    """Exception raised when company data is invalid."""

    def __init__(self, message: str):
        """
        Initialize exception.

        Args:
            message: Description of what is invalid
        """
        super().__init__(f"Invalid company: {message}")
