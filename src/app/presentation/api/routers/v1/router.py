"""
API v1 Router.

Combines all v1 routers (cross-country, CO, MX).
"""

from fastapi import APIRouter

from app.presentation.api.routers.v1.cross.companies import router as companies_router

# Create v1 router
router = APIRouter()

# Include cross-country routers
router.include_router(companies_router, prefix="")

# TODO: Include country-specific routers when needed
# from presentation.api.routers.v1.co import users as co_users
# from presentation.api.routers.v1.mx import users as mx_users
# router.include_router(co_users.router, prefix="/co")
# router.include_router(mx_users.router, prefix="/mx")
