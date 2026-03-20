"""Pydantic schemas for Ticket model"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional


class TicketBase(BaseModel):
    """Base schema for Ticket with common fields"""

    id_pedido: str = Field(..., max_length=100, description="Order ID")
    id_cliente: str = Field(..., max_length=100, description="Customer ID")
    fecha: date = Field(..., description="Transaction date")
    hora: time = Field(..., description="Transaction time")
    id_departamento: str = Field(..., max_length=50, description="Department ID")
    id_seccion: str = Field(..., max_length=50, description="Section ID")
    id_producto: str = Field(..., max_length=100, description="Product ID")
    nombre_producto: str = Field(..., max_length=500, description="Product name")
    precio_unitario: Decimal = Field(..., ge=0, decimal_places=2, description="Unit price")
    cantidad: int = Field(..., gt=0, description="Quantity")
    precio_total: Decimal = Field(..., ge=0, decimal_places=2, description="Total price")


class TicketCreate(TicketBase):
    """Schema for creating a new Ticket"""
    pass


class TicketResponse(TicketBase):
    """Schema for Ticket responses"""

    id: int = Field(..., description="Ticket ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
