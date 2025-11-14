"""
Company Types ORM Models.

SQLAlchemy models for company_types and company_company_type tables.
"""

from sqlalchemy import Column, String, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.infrastructure.database.postgres.models.base import BaseModel


class CompanyTypeModel(BaseModel):
    """
    ORM Model for company_types table.

    Represents different types/categories of companies.
    """

    __tablename__ = "company_types"

    company_types_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    type_name = Column(String(255), nullable=False, unique=True, index=True)

    # Relationship through association table
    companies = relationship(
        "CompanyModel", secondary="company_company_type", back_populates="company_types"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<CompanyTypeModel(id={self.company_types_id}, name={self.type_name})>"


class CompanyCompanyTypeModel(BaseModel):
    """
    ORM Model for company_company_type table.

    Association table for many-to-many relationship between companies and company types.
    """

    __tablename__ = "company_company_type"

    company_company_type_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.company_id"), nullable=False, index=True)
    company_types_id = Column(
        UUID(as_uuid=True), ForeignKey("company_types.company_types_id"), nullable=False, index=True
    )
    percentage = Column(Numeric, nullable=True)
    company_relation = Column(String(255), nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<CompanyCompanyTypeModel(company_id={self.company_id}, "
            f"type_id={self.company_types_id}, percentage={self.percentage})>"
        )
