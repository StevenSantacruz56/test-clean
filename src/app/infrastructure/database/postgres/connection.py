"""
PostgreSQL Database Connection.

Configuration and connection management for PostgreSQL.
"""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

# Database URL will be loaded from settings
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/testclean"


def get_async_engine(
    database_url: str = DATABASE_URL,
    echo: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
) -> AsyncEngine:
    """
    Create async SQLAlchemy engine.

    Args:
        database_url: PostgreSQL connection URL
        echo: Echo SQL statements
        pool_size: Connection pool size
        max_overflow: Max overflow connections

    Returns:
        AsyncEngine: SQLAlchemy async engine
    """
    return create_async_engine(
        database_url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
    )


# Create global engine instance
engine = get_async_engine()
