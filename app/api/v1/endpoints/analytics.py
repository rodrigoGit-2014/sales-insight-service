"""Analytics endpoints"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    DepartmentAnalyticsResponse,
    SectionAnalyticsResponse,
    ProductAnalyticsResponse,
    CustomerAnalyticsResponse,
    AverageSpendResponse,
    OrderStatsResponse
)

router = APIRouter()


@router.get(
    "/analytics/departments",
    response_model=DepartmentAnalyticsResponse,
    summary="Get department analytics",
    description="Get sales analytics grouped by department"
)
def get_department_analytics(
    db: Session = Depends(get_db)
):
    """
    Get sales analytics by department.

    Returns for each department:
    - Total sales
    - Order count
    - Percentage of total sales

    Results are ordered by total sales (highest first).
    """
    analytics_service = AnalyticsService(db)

    try:
        result = analytics_service.get_department_analytics()
        return DepartmentAnalyticsResponse(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate department analytics: {str(e)}"
        )


@router.get(
    "/analytics/sections",
    response_model=SectionAnalyticsResponse,
    summary="Get section analytics",
    description="Get sales analytics grouped by section"
)
def get_section_analytics(
    db: Session = Depends(get_db)
):
    """
    Get sales analytics by section.

    Returns for each section:
    - Section ID
    - Department ID
    - Total sales
    - Order count
    - Percentage of total sales

    Results are ordered by total sales (highest first).
    """
    analytics_service = AnalyticsService(db)

    try:
        result = analytics_service.get_section_analytics()
        return SectionAnalyticsResponse(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate section analytics: {str(e)}"
        )


@router.get(
    "/analytics/products/top-quantity",
    response_model=ProductAnalyticsResponse,
    summary="Get top products by quantity",
    description="Get products with highest quantity sold"
)
def get_top_products_by_quantity(
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    db: Session = Depends(get_db)
):
    """
    Get top products by quantity sold.

    Returns for each product:
    - Product ID and name
    - Total quantity sold
    - Total revenue
    - Order count
    - Average unit price

    Results are ordered by quantity (highest first).
    """
    analytics_service = AnalyticsService(db)

    try:
        result = analytics_service.get_top_products_by_quantity(limit)
        return ProductAnalyticsResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate top products: {str(e)}"
        )


@router.get(
    "/analytics/products/top-revenue",
    response_model=ProductAnalyticsResponse,
    summary="Get top products by revenue",
    description="Get products with highest revenue"
)
def get_top_products_by_revenue(
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    db: Session = Depends(get_db)
):
    """
    Get top products by revenue.

    Returns for each product:
    - Product ID and name
    - Total quantity sold
    - Total revenue
    - Order count
    - Average unit price

    Results are ordered by revenue (highest first).
    """
    analytics_service = AnalyticsService(db)

    try:
        result = analytics_service.get_top_products_by_revenue(limit)
        return ProductAnalyticsResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate top products: {str(e)}"
        )


@router.get(
    "/analytics/customers/top",
    response_model=CustomerAnalyticsResponse,
    summary="Get top customers",
    description="Get customers with highest total spend"
)
def get_top_customers(
    limit: int = Query(20, ge=1, le=100, description="Number of customers to return"),
    db: Session = Depends(get_db)
):
    """
    Get top customers by total spend.

    Returns for each customer:
    - Customer ID
    - Total amount spent
    - Order count
    - Average order value
    - First and last purchase dates

    Results are ordered by total spend (highest first).
    """
    analytics_service = AnalyticsService(db)

    try:
        result = analytics_service.get_top_customers(limit)
        return CustomerAnalyticsResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate top customers: {str(e)}"
        )


@router.get(
    "/analytics/customers/average-spend",
    response_model=AverageSpendResponse,
    summary="Get average customer spend",
    description="Calculate average spend per customer"
)
def get_customer_average_spend(
    db: Session = Depends(get_db)
):
    """
    Get average spend per customer.

    Returns:
    - Average spend per customer
    - Total number of customers
    - Total sales amount
    """
    analytics_service = AnalyticsService(db)

    try:
        result = analytics_service.get_customer_average_spend()
        return AverageSpendResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate average spend: {str(e)}"
        )


@router.get(
    "/analytics/orders/count",
    response_model=OrderStatsResponse,
    summary="Get total order count",
    description="Get total number of orders"
)
def get_order_count(
    db: Session = Depends(get_db)
):
    """
    Get order statistics.

    Returns:
    - Total number of orders
    - Average order value
    - Total sales amount
    """
    analytics_service = AnalyticsService(db)

    try:
        result = analytics_service.get_order_statistics()
        return OrderStatsResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate order statistics: {str(e)}"
        )


@router.get(
    "/analytics/orders/average-value",
    response_model=OrderStatsResponse,
    summary="Get average order value",
    description="Calculate average order value"
)
def get_average_order_value(
    db: Session = Depends(get_db)
):
    """
    Get average order value.

    Returns:
    - Total number of orders
    - Average order value
    - Total sales amount
    """
    analytics_service = AnalyticsService(db)

    try:
        result = analytics_service.get_order_statistics()
        return OrderStatsResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate order statistics: {str(e)}"
        )
