"""
SQLAlchemy Base Model.

Base declarative model for all ORM models.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common fields.

    All models inherit from this to get created_at and updated_at timestamps.
    """

    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}>"
