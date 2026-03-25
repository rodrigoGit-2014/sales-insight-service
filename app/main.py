"""FastAPI application entry point"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import (
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from app.api.v1.router import api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-ready FastAPI backend for sales analytics with "
        "asynchronous CSV processing and comprehensive analytics endpoints."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API router
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)


def _create_matview_trigger(engine):
    """Create a PostgreSQL trigger that refreshes materialized views on tickets changes"""
    from sqlalchemy import text

    trigger_sql = """
    CREATE OR REPLACE FUNCTION refresh_sales_matviews()
    RETURNS TRIGGER AS $$
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_trend;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_analytics;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_section_analytics;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_product_analytics;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_top;
        RETURN NULL;
    EXCEPTION WHEN OTHERS THEN
        REFRESH MATERIALIZED VIEW mv_daily_sales;
        REFRESH MATERIALIZED VIEW mv_monthly_trend;
        REFRESH MATERIALIZED VIEW mv_department_analytics;
        REFRESH MATERIALIZED VIEW mv_section_analytics;
        REFRESH MATERIALIZED VIEW mv_product_analytics;
        REFRESH MATERIALIZED VIEW mv_customer_top;
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_refresh_sales_matviews ON tickets;

    CREATE TRIGGER trg_refresh_sales_matviews
    AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE
    ON tickets
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_sales_matviews();
    """
    with engine.connect() as conn:
        conn.execute(text(trigger_sql))
        conn.commit()
    logger.info("Materialized view trigger created on tickets table")


def _refresh_matviews_on_startup(engine):
    """Refresh materialized views so they reflect existing data after DB reset or restart."""
    from sqlalchemy import text

    views = [
        "mv_daily_sales", "mv_monthly_trend", "mv_department_analytics",
        "mv_section_analytics", "mv_product_analytics", "mv_customer_top",
    ]
    try:
        with engine.connect() as conn:
            for view in views:
                try:
                    conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
                except Exception:
                    pass
            conn.commit()
        logger.info("Materialized views refreshed on startup")
    except Exception as e:
        logger.warning(f"Could not refresh materialized views on startup: {e}")


@app.on_event("startup")
async def startup_event():
    """Execute on application startup"""
    from app.db.session import create_tables, create_materialized_views, engine
    create_tables()
    create_materialized_views()
    try:
        _create_matview_trigger(engine)
    except Exception as e:
        logger.warning(f"Could not create matview trigger: {e}")
    _refresh_matviews_on_startup(engine)
    logger.info(
        f"Starting {settings.APP_NAME} v{settings.APP_VERSION}",
        extra={
            "environment": "development" if settings.DEBUG else "production",
            "log_level": settings.LOG_LEVEL
        }
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown"""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Root endpoint",
    description="Welcome message and API information"
)
def root():
    """
    Root endpoint.

    Returns basic API information and links to documentation.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_PREFIX
    }


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Health check",
    description="Check if the API is running"
)
def health_check():
    """
    Health check endpoint.

    Returns the current status of the API.
    Use this for monitoring and load balancer health checks.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get(
    "/readiness",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Readiness check",
    description="Check if the API is ready to accept requests"
)
def readiness_check():
    """
    Readiness check endpoint.

    Verifies that the API is ready to handle requests.
    This could include checking database connectivity, etc.
    """
    # In a production environment, you might want to:
    # - Check database connection
    # - Check Redis connection
    # - Check other critical dependencies

    return {
        "status": "ready",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get(
    "/celery-health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Celery health check",
    description="Check Celery worker connectivity and queue status"
)
def celery_health_check():
    """
    Celery health check endpoint.

    Checks if Celery workers are connected and can process tasks.
    """
    from celery_app.celery import celery_app

    try:
        # Check if workers are available
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        registered_tasks = inspect.registered()

        if not active_workers:
            return {
                "status": "unhealthy",
                "message": "No Celery workers are running",
                "active_workers": 0,
                "broker_url": settings.CELERY_BROKER_URL.split('@')[-1] if '@' in settings.CELERY_BROKER_URL else "configured"
            }

        return {
            "status": "healthy",
            "active_workers": len(active_workers),
            "workers": list(active_workers.keys()),
            "registered_tasks": list(registered_tasks.values())[0] if registered_tasks else [],
            "broker_url": settings.CELERY_BROKER_URL.split('@')[-1] if '@' in settings.CELERY_BROKER_URL else "configured"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to Celery: {str(e)}",
            "broker_url": settings.CELERY_BROKER_URL.split('@')[-1] if '@' in settings.CELERY_BROKER_URL else "configured"
        }


@app.get(
    "/db-health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Database and materialized views health check",
    description="Check database connectivity and materialized views status"
)
def db_health_check():
    """
    Database health check endpoint.

    Checks database connectivity and materialized views status.
    """
    from sqlalchemy import text
    from app.db.session import engine

    try:
        with engine.connect() as conn:
            # Check database connectivity
            conn.execute(text("SELECT 1"))

            # Check tickets table
            result = conn.execute(text("SELECT COUNT(*) FROM tickets"))
            ticket_count = result.scalar()

            # Check materialized views
            result = conn.execute(text("""
                SELECT matviewname,
                       pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
                FROM pg_matviews
                WHERE schemaname = 'public'
                ORDER BY matviewname
            """))
            views = [{"name": row[0], "size": row[1]} for row in result.fetchall()]

            # Check if all required views exist
            required_views = {
                'mv_daily_sales',
                'mv_monthly_trend',
                'mv_department_analytics',
                'mv_section_analytics',
                'mv_product_analytics',
                'mv_customer_top'
            }
            existing_views = {v['name'] for v in views}
            missing_views = required_views - existing_views

            return {
                "status": "healthy" if not missing_views else "degraded",
                "database": "connected",
                "ticket_count": ticket_count,
                "materialized_views": {
                    "total": len(views),
                    "required": len(required_views),
                    "missing": list(missing_views) if missing_views else [],
                    "views": views
                },
                "message": "All systems operational" if not missing_views else f"Missing views: {', '.join(missing_views)}"
            }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "message": f"Database error: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
