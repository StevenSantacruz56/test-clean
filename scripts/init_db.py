"""
Initialize Database.

Script to create database tables.
"""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.database.postgres.connection import engine
from app.infrastructure.database.postgres.models.base import Base
from app.infrastructure.database.postgres.models.company_model import CompanyModel
from app.infrastructure.database.postgres.models.company_detail_model import CompanyDetailModel
from app.infrastructure.database.postgres.models.company_type_model import CompanyTypeModel, CompanyCompanyTypeModel


async def init_db():
    """
    Initialize database by creating all tables.

    This will create all tables defined in the models.
    """
    print("Creating database tables...")

    async with engine.begin() as conn:
        # Drop all tables (use with caution!)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully!")
    print(f"Created tables: {', '.join(Base.metadata.tables.keys())}")


async def main():
    """Main function."""
    try:
        await init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
