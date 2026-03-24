"""Database session management with SQLAlchemy"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Maximum number of connections to keep in pool
    max_overflow=10,  # Maximum number of connections to create beyond pool_size
    echo=settings.DEBUG,  # Log SQL statements in debug mode
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields:
        Session: SQLAlchemy database session

    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables defined in models (for testing/development)"""
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)


def create_materialized_views():
    """
    Create materialized views if they don't exist.
    This function is idempotent and safe to call on every startup.
    """
    try:
        # Check if materialized views already exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM pg_matviews
                WHERE schemaname = 'public'
                AND matviewname IN (
                    'mv_daily_sales',
                    'mv_monthly_trend',
                    'mv_department_analytics',
                    'mv_section_analytics',
                    'mv_product_analytics',
                    'mv_customer_top'
                )
            """))
            existing_views = result.scalar()

            # If all 6 views exist, skip creation
            if existing_views == 6:
                logger.info("All materialized views already exist")
                return

            logger.info(f"Creating materialized views (found {existing_views}/6 views)...")

            # Read and execute the SQL file
            sql_file = Path(__file__).parent.parent.parent / "docker" / "postgres" / "create_materialized_views.sql"

            if not sql_file.exists():
                logger.warning(f"Materialized views SQL file not found at {sql_file}")
                return

            with open(sql_file, 'r') as f:
                sql_content = f.read()

            # Execute the SQL
            conn.execute(text(sql_content))
            conn.commit()

            logger.info("✓ Materialized views created successfully")

    except Exception as e:
        logger.error(f"Failed to create materialized views: {e}")
        # Don't fail the application startup if view creation fails
        pass


def drop_tables():
    """Drop all tables (for testing)"""
    from app.db.base import Base
    Base.metadata.drop_all(bind=engine)
