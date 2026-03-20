"""Sales analytics endpoints"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.api.deps import get_db
from app.services.sales_service import SalesService
from app.schemas.sales import SalesTotalResponse, MonthlyTrendResponse

router = APIRouter()


@router.get(
    "/sales/total",
    response_model=SalesTotalResponse,
    summary="Get total sales",
    description="Calculate total sales for a date range"
)
def get_total_sales(
    fecha_inicio: Optional[date] = Query(
        None,
        description="Start date (inclusive). Format: YYYY-MM-DD"
    ),
    fecha_fin: Optional[date] = Query(
        None,
        description="End date (inclusive). Format: YYYY-MM-DD"
    ),
    db: Session = Depends(get_db)
):
    """
    Get total sales for a date range.

    Returns:
    - total_sales: Sum of all sales
    - total_orders: Number of distinct orders
    - average_order_value: Average value per order

    If no dates are provided, returns totals for all data.
    """
    # Validate date range
    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fecha_inicio must be before or equal to fecha_fin"
        )

    sales_service = SalesService(db)

    try:
        result = sales_service.get_total_sales(fecha_inicio, fecha_fin)
        return SalesTotalResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate total sales: {str(e)}"
        )


@router.get(
    "/sales/monthly-trend",
    response_model=MonthlyTrendResponse,
    summary="Get monthly sales trend",
    description="Get sales aggregated by month"
)
def get_monthly_trend(
    db: Session = Depends(get_db)
):
    """
    Get monthly sales trend.

    Returns sales data grouped by year and month, including:
    - Total sales per month
    - Order count per month
    - Average order value per month

    Data is ordered chronologically (oldest first).
    """
    sales_service = SalesService(db)

    try:
        result = sales_service.get_monthly_trend()
        return MonthlyTrendResponse(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate monthly trend: {str(e)}"
        )
