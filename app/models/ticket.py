"""Ticket model representing sales transactions"""

from sqlalchemy import Column, BigInteger, String, Date, Time, Numeric, Integer, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
from datetime import date, time
from decimal import Decimal

from app.db.base import Base


class Ticket(Base):
    """
    Sales ticket/transaction model.

    Represents a single sales transaction with product, customer,
    pricing, and timestamp information.
    """

    __tablename__ = "tickets"

    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)

    # Tenant
    company_id = Column(PGUUID(as_uuid=True), nullable=False, index=True, comment="Company/tenant ID")

    # Transaction Identifiers
    id_pedido = Column(String(100), nullable=False, comment="Order ID")
    id_cliente = Column(String(100), nullable=False, index=True, comment="Customer ID")

    # Timestamp Information
    fecha = Column(Date, nullable=False, index=True, comment="Transaction date")
    hora = Column(Time, nullable=False, comment="Transaction time")

    # Organization Structure
    id_departamento = Column(String(50), nullable=False, index=True, comment="Department ID")
    id_seccion = Column(String(50), nullable=False, index=True, comment="Section ID")

    # Product Information
    id_producto = Column(String(100), nullable=False, index=True, comment="Product ID")
    nombre_producto = Column(String(500), nullable=False, comment="Product name")

    # Pricing Information
    precio_unitario = Column(
        Numeric(12, 2),
        nullable=False,
        comment="Unit price"
    )
    cantidad = Column(Integer, nullable=False, comment="Quantity sold")
    precio_total = Column(
        Numeric(12, 2),
        nullable=False,
        comment="Total price (precio_unitario * cantidad)"
    )

    # Audit Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last update timestamp"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint('precio_unitario >= 0', name='chk_precio_unitario_positive'),
        CheckConstraint('cantidad > 0', name='chk_cantidad_positive'),
        CheckConstraint('precio_total >= 0', name='chk_precio_total_positive'),
    )

    def __repr__(self) -> str:
        return (
            f"<Ticket(id={self.id}, pedido={self.id_pedido}, "
            f"cliente={self.id_cliente}, producto={self.nombre_producto}, "
            f"total={self.precio_total})>"
        )

    @classmethod
    def from_csv_row(cls, row: dict) -> "Ticket":
        """
        Create a Ticket instance from a CSV row dictionary.

        Args:
            row: Dictionary with CSV column names as keys

        Returns:
            Ticket instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            return cls(
                id_pedido=str(row['id_pedido']),
                id_cliente=str(row['id_cliente']),
                fecha=row['fecha'] if isinstance(row['fecha'], date) else date.fromisoformat(str(row['fecha'])),
                hora=row['hora'] if isinstance(row['hora'], time) else time.fromisoformat(str(row['hora'])),
                id_departamento=str(row['id_departamento']),
                id_seccion=str(row['id_seccion']),
                id_producto=str(row['id_producto']),
                nombre_producto=str(row['nombre_producto']),
                precio_unitario=Decimal(str(row['precio_unitario'])),
                cantidad=int(row['cantidad']),
                precio_total=Decimal(str(row['precio_total']))
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Invalid CSV row data: {e}")
