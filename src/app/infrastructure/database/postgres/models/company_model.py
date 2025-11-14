"""
Company ORM Model.

SQLAlchemy model for the company table.
"""

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.infrastructure.database.postgres.models.base import BaseModel


class CompanyModel(BaseModel):
    """
    ORM Model for company table.

    Maps to the 'company' table in PostgreSQL.
    """

    __tablename__ = "company"

    company_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, unique=True, index=True)
    country_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Relationships
    details = relationship("CompanyDetailModel", back_populates="company", cascade="all, delete-orphan")
    company_types = relationship(
        "CompanyTypeModel", secondary="company_company_type", back_populates="companies"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<CompanyModel(id={self.company_id}, name={self.company_name})>"
