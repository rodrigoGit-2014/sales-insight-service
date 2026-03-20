"""Pydantic schemas for request/response validation"""

from app.schemas.ticket import TicketBase, TicketCreate, TicketResponse
from app.schemas.job import JobResponse, JobCreate
from app.schemas.sales import SalesTotalResponse, MonthlyTrendResponse, MonthlyTrendItem
from app.schemas.analytics import (
    DepartmentAnalyticsResponse,
    DepartmentAnalyticsItem,
    SectionAnalyticsResponse,
    SectionAnalyticsItem,
    ProductAnalyticsItem,
    ProductAnalyticsResponse,
    CustomerAnalyticsItem,
    CustomerAnalyticsResponse,
    AverageSpendResponse,
    OrderStatsResponse
)

__all__ = [
    "TicketBase",
    "TicketCreate",
    "TicketResponse",
    "JobResponse",
    "JobCreate",
    "SalesTotalResponse",
    "MonthlyTrendResponse",
    "MonthlyTrendItem",
    "DepartmentAnalyticsResponse",
    "DepartmentAnalyticsItem",
    "SectionAnalyticsResponse",
    "SectionAnalyticsItem",
    "ProductAnalyticsItem",
    "ProductAnalyticsResponse",
    "CustomerAnalyticsItem",
    "CustomerAnalyticsResponse",
    "AverageSpendResponse",
    "OrderStatsResponse",
]
