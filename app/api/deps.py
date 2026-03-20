"""Dependency injection for API endpoints"""

from typing import Generator
from sqlalchemy.orm import Session

from app.db.session import get_db

# Re-export for convenience
__all__ = ["get_db"]
