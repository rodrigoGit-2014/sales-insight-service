"""SQLAlchemy declarative base"""

from sqlalchemy.ext.declarative import declarative_base

# Create declarative base for SQLAlchemy models
Base = declarative_base()

# NOTE: Models import Base from here and register themselves automatically.
# Do NOT import models here to avoid circular imports.
# For Alembic migrations, import models in alembic/env.py instead.
