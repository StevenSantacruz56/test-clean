"""
PostgreSQL Session Management.

Async session factory for database operations.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.database.postgres.connection import engine

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.

    Yields:
        AsyncSession: Database session

    Usage:
        async with get_db_session() as session:
            # Use session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
