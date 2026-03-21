"""Main API v1 router aggregating all endpoints"""

from fastapi import APIRouter

from app.api.v1.endpoints import upload, jobs, sales, analytics, config

# Create main API v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    upload.router,
    tags=["Upload"]
)

api_router.include_router(
    jobs.router,
    tags=["Jobs"]
)

api_router.include_router(
    sales.router,
    tags=["Sales"]
)

api_router.include_router(
    analytics.router,
    tags=["Analytics"]
)

api_router.include_router(
    config.router,
    tags=["Configuration"]
)
