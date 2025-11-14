"""
Company Detail ORM Model.

SQLAlchemy model for the company_detail table.
"""

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.infrastructure.database.postgres.models.base import BaseModel


class CompanyDetailModel(BaseModel):
    """
    ORM Model for company_detail table.

    Stores detailed information about a company including
    identification, contact details, and verification status.
    """

    __tablename__ = "company_detail"

    company_detail_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.company_id"), nullable=False, index=True)
    identification_type_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    identity_number = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    number_indicative = Column(String(255), nullable=True)
    phone_number = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    city_id = Column(UUID(as_uuid=True), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    person_type = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    verified = Column(Boolean, default=False, nullable=False)

    # Relationship
    company = relationship("CompanyModel", back_populates="details")

    def __repr__(self) -> str:
        """String representation."""
        return f"<CompanyDetailModel(id={self.company_detail_id}, identity={self.identity_number})>"
