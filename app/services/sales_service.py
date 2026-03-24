"""Service for sales analytics calculations"""

from typing import Dict, List, Any, Optional
from datetime import date
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.ticket_repository import TicketRepository


class SalesService:
    """Service for sales-related business logic and calculations"""

    def __init__(self, db: Session):
        self.db = db
        self.ticket_repository = TicketRepository(db)

    def get_total_sales(
        self,
        company_id: UUID,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get total sales for a date range.

        Args:
            company_id: Company/tenant UUID
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            Dictionary with sales totals and statistics
        """
        result = self.ticket_repository.get_total_sales(company_id, fecha_inicio, fecha_fin)

        # Add date range to response
        result['fecha_inicio'] = fecha_inicio
        result['fecha_fin'] = fecha_fin

        return result

    def get_monthly_trend(
        self,
        company_id: UUID,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get monthly sales trend.

        Args:
            company_id: Company/tenant UUID
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            List of monthly sales data
        """
        return self.ticket_repository.get_monthly_trend(company_id, fecha_inicio, fecha_fin)

    def get_sales_by_date_range(
        self,
        company_id: UUID,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Dict[str, Any]:
        """
        Get detailed sales information for a date range.

        Args:
            company_id: Company/tenant UUID
            fecha_inicio: Start date
            fecha_fin: End date

        Returns:
            Dictionary with detailed sales data
        """
        sales_data = self.ticket_repository.get_total_sales(company_id, fecha_inicio, fecha_fin)

        # Calculate additional metrics
        days_in_range = (fecha_fin - fecha_inicio).days + 1
        avg_daily_sales = sales_data['total_sales'] / days_in_range if days_in_range > 0 else 0

        return {
            **sales_data,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'days_in_range': days_in_range,
            'average_daily_sales': avg_daily_sales
        }
