"""Database session management with SQLAlchemy"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

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


def drop_tables():
    """Drop all tables (for testing)"""
    from app.db.base import Base
    Base.metadata.drop_all(bind=engine)
