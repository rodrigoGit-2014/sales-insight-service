"""Seccion model for category configuration"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class Seccion(Base):
    """Section category with associated icon."""

    __tablename__ = "secciones"

    id_seccion = Column(Integer, primary_key=True, autoincrement=False)
    nombre = Column(String(200), nullable=False)
    icono_name = Column(String(100), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Seccion(id={self.id_seccion}, nombre={self.nombre})>"
