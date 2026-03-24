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
    """Create all tables defined in models and run migrations for new columns."""
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)
    _run_migrations()


def _run_migrations():
    """Add missing columns to existing tables (lightweight migration)."""
    from app.db.base import Base

    try:
        with engine.connect() as conn:
            # Tables that need company_id added as a regular column
            for table_name in ['tickets', 'jobs']:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = :table_name
                    AND column_name = 'company_id'
                """), {"table_name": table_name})

                # Check if table exists first
                table_exists = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = :table_name
                """), {"table_name": table_name}).scalar() > 0

                if table_exists and result.scalar() == 0:
                    logger.info(f"Adding company_id column to {table_name}")
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN company_id UUID"))
                    conn.execute(text(
                        f"CREATE INDEX IF NOT EXISTS ix_{table_name}_company_id ON {table_name}(company_id)"
                    ))
                    conn.commit()
                    logger.info(f"Added company_id to {table_name}")

            # Tables where company_id is part of the primary key (need full recreate)
            for table_name in ['secciones', 'departamentos']:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = :table_name
                    AND column_name = 'company_id'
                """), {"table_name": table_name})

                table_exists = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = :table_name
                """), {"table_name": table_name}).scalar() > 0

                if table_exists and result.scalar() == 0:
                    logger.info(f"Recreating {table_name} with company_id in primary key")
                    conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
                    conn.commit()
                    # create_all will recreate it with the correct schema
                    Base.metadata.tables[table_name].create(bind=engine)
                    logger.info(f"Recreated {table_name}")

    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")


def _split_sql_statements(sql_content: str) -> list:
    """
    Split SQL content into individual statements, correctly handling $$ blocks.
    """
    statements = []
    current = []
    in_dollar_block = False

    for line in sql_content.split('\n'):
        stripped = line.strip()

        # Skip pure comment lines outside of $$ blocks
        if stripped.startswith('--') and not in_dollar_block:
            continue

        # Track $$ block boundaries
        dollar_count = line.count('$$')
        if dollar_count % 2 == 1:
            in_dollar_block = not in_dollar_block

        current.append(line)

        # If line ends with ; and we're not inside a $$ block, it's a statement boundary
        if stripped.endswith(';') and not in_dollar_block:
            stmt = '\n'.join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []

    # Handle any remaining content
    if current:
        stmt = '\n'.join(current).strip()
        if stmt:
            statements.append(stmt)

    return statements


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

            # Check if views have company_id column (needed for multi-tenant filtering)
            has_company_id = False
            if existing_views == 6:
                col_result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = 'mv_product_analytics'
                    AND column_name = 'company_id'
                """))
                has_company_id = col_result.scalar() > 0

            # If all 6 views exist and have company_id, skip creation
            if existing_views == 6 and has_company_id:
                logger.info("All materialized views already exist and are up to date")
                return

            logger.info(f"Creating materialized views (found {existing_views}/6 views)...")

            # Read and execute the SQL file
            sql_file = Path(__file__).parent.parent.parent / "docker" / "postgres" / "create_materialized_views.sql"

            if not sql_file.exists():
                logger.warning(f"Materialized views SQL file not found at {sql_file}")
                return

            with open(sql_file, 'r') as f:
                sql_content = f.read()

            # Execute each statement separately to avoid issues with $$ blocks
            # Split on semicolons but preserve $$ function bodies
            statements = _split_sql_statements(sql_content)
            for stmt in statements:
                stmt = stmt.strip()
                if stmt and not stmt.startswith('--'):
                    conn.execute(text(stmt))
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
