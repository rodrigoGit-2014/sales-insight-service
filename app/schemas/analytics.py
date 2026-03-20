"""Pydantic schemas for analytics endpoints"""

from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import List, Optional


class DepartmentAnalyticsItem(BaseModel):
    """Analytics data for a single department"""

    id_departamento: str = Field(..., description="Department ID")
    total_sales: Decimal = Field(..., description="Total sales amount")
    order_count: int = Field(..., description="Number of orders")
    percentage_of_total: Optional[Decimal] = Field(None, description="Percentage of total sales")


class DepartmentAnalyticsResponse(BaseModel):
    """Response schema for department analytics"""

    data: List[DepartmentAnalyticsItem] = Field(..., description="Department analytics data")


class SectionAnalyticsItem(BaseModel):
    """Analytics data for a single section"""

    id_seccion: str = Field(..., description="Section ID")
    id_departamento: str = Field(..., description="Department ID")
    total_sales: Decimal = Field(..., description="Total sales amount")
    order_count: int = Field(..., description="Number of orders")
    percentage_of_total: Optional[Decimal] = Field(None, description="Percentage of total sales")


class SectionAnalyticsResponse(BaseModel):
    """Response schema for section analytics"""

    data: List[SectionAnalyticsItem] = Field(..., description="Section analytics data")


class ProductAnalyticsItem(BaseModel):
    """Analytics data for a single product"""

    id_producto: str = Field(..., description="Product ID")
    nombre_producto: str = Field(..., description="Product name")
    total_quantity: int = Field(..., description="Total quantity sold")
    total_revenue: Decimal = Field(..., description="Total revenue")
    order_count: int = Field(..., description="Number of orders")
    avg_unit_price: Optional[Decimal] = Field(None, description="Average unit price")


class ProductAnalyticsResponse(BaseModel):
    """Response schema for product analytics"""

    data: List[ProductAnalyticsItem] = Field(..., description="Product analytics data")
    limit: int = Field(..., description="Limit applied to results")


class CustomerAnalyticsItem(BaseModel):
    """Analytics data for a single customer"""

    id_cliente: str = Field(..., description="Customer ID")
    total_spent: Decimal = Field(..., description="Total amount spent")
    order_count: int = Field(..., description="Number of orders")
    average_order_value: Decimal = Field(..., description="Average order value")
    first_purchase: Optional[date] = Field(None, description="Date of first purchase")
    last_purchase: Optional[date] = Field(None, description="Date of last purchase")


class CustomerAnalyticsResponse(BaseModel):
    """Response schema for customer analytics"""

    data: List[CustomerAnalyticsItem] = Field(..., description="Customer analytics data")
    limit: int = Field(..., description="Limit applied to results")


class AverageSpendResponse(BaseModel):
    """Response schema for average customer spend"""

    average_spend_per_customer: Decimal = Field(..., description="Average spend per customer")
    total_customers: int = Field(..., description="Total number of customers")
    total_sales: Decimal = Field(..., description="Total sales amount")


class OrderStatsResponse(BaseModel):
    """Response schema for order statistics"""

    total_orders: int = Field(..., description="Total number of orders")
    average_order_value: Decimal = Field(..., description="Average order value")
    total_sales: Decimal = Field(..., description="Total sales amount")
