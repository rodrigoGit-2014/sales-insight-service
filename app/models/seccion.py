"""Seccion model for category configuration"""

from sqlalchemy import Column, Integer, String, DateTime, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

from app.db.base import Base


class Seccion(Base):
    """Section category with associated icon."""

    __tablename__ = "secciones"

    company_id = Column(PGUUID(as_uuid=True), nullable=False, comment="Company/tenant ID")
    id_seccion = Column(Integer, nullable=False, autoincrement=False)
    nombre = Column(String(200), nullable=False)
    icono_name = Column(String(100), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        PrimaryKeyConstraint("company_id", "id_seccion"),
    )

    def __repr__(self) -> str:
        return f"<Seccion(id={self.id_seccion}, nombre={self.nombre})>"
