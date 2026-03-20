"""Pydantic schemas for sales analytics"""

from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import List


class SalesTotalResponse(BaseModel):
    """Response schema for total sales endpoint"""

    fecha_inicio: date = Field(..., description="Start date")
    fecha_fin: date = Field(..., description="End date")
    total_sales: Decimal = Field(..., description="Total sales amount")
    total_orders: int = Field(..., description="Total number of orders")
    average_order_value: Decimal = Field(..., description="Average order value")


class MonthlyTrendItem(BaseModel):
    """Single month data point for monthly trend"""

    year: int = Field(..., description="Year")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    total_sales: Decimal = Field(..., description="Total sales for the month")
    order_count: int = Field(..., description="Number of orders")
    avg_order_value: Decimal = Field(..., description="Average order value")


class MonthlyTrendResponse(BaseModel):
    """Response schema for monthly trend endpoint"""

    data: List[MonthlyTrendItem] = Field(..., description="Monthly trend data")
