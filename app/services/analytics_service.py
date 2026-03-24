"""Service for analytics calculations"""

from typing import Dict, List, Any, Optional
from datetime import date
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.ticket_repository import TicketRepository


class AnalyticsService:
    """Service for analytics-related business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.ticket_repository = TicketRepository(db)

    def get_department_analytics(
        self,
        company_id: UUID,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get analytics grouped by department.

        Args:
            company_id: Company/tenant UUID
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            List of department analytics data
        """
        return self.ticket_repository.get_department_analytics(company_id, fecha_inicio, fecha_fin)

    def get_section_analytics(
        self,
        company_id: UUID,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get analytics grouped by section.

        Args:
            company_id: Company/tenant UUID
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            List of section analytics data
        """
        return self.ticket_repository.get_section_analytics(company_id, fecha_inicio, fecha_fin)

    def get_top_products_by_quantity(
        self,
        company_id: UUID,
        limit: int = 10,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get top products by quantity sold.

        Args:
            company_id: Company/tenant UUID
            limit: Number of top products to return
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            Dictionary with product data and limit
        """
        products = self.ticket_repository.get_top_products_by_quantity(company_id, limit, fecha_inicio, fecha_fin)
        return {
            'data': products,
            'limit': limit
        }

    def get_top_products_by_revenue(
        self,
        company_id: UUID,
        limit: int = 10,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get top products by revenue.

        Args:
            company_id: Company/tenant UUID
            limit: Number of top products to return
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            Dictionary with product data and limit
        """
        products = self.ticket_repository.get_top_products_by_revenue(company_id, limit, fecha_inicio, fecha_fin)
        return {
            'data': products,
            'limit': limit
        }

    def get_top_customers(
        self,
        company_id: UUID,
        limit: int = 20,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get top customers by total spend.

        Args:
            company_id: Company/tenant UUID
            limit: Number of top customers to return
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            Dictionary with customer data and limit
        """
        customers = self.ticket_repository.get_top_customers(company_id, limit, fecha_inicio, fecha_fin)
        return {
            'data': customers,
            'limit': limit
        }

    def get_customer_average_spend(
        self,
        company_id: UUID,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get average spend per customer.

        Args:
            company_id: Company/tenant UUID
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            Dictionary with average spend statistics
        """
        return self.ticket_repository.get_customer_average_spend(company_id, fecha_inicio, fecha_fin)

    def get_order_statistics(
        self,
        company_id: UUID,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get overall order statistics.

        Args:
            company_id: Company/tenant UUID
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            Dictionary with order count, average value, and total sales
        """
        order_count = self.ticket_repository.get_order_count(company_id, fecha_inicio, fecha_fin)
        avg_order_value = self.ticket_repository.get_average_order_value(company_id, fecha_inicio, fecha_fin)
        total_sales = order_count * avg_order_value if order_count > 0 else Decimal('0')

        return {
            'total_orders': order_count,
            'average_order_value': avg_order_value,
            'total_sales': total_sales
        }

    def get_product_performance_summary(self, company_id: UUID, limit: int = 10) -> Dict[str, Any]:
        """
        Get comprehensive product performance summary.

        Args:
            company_id: Company/tenant UUID
            limit: Number of top products to include

        Returns:
            Dictionary with top products by quantity and revenue
        """
        top_by_quantity = self.ticket_repository.get_top_products_by_quantity(company_id, limit)
        top_by_revenue = self.ticket_repository.get_top_products_by_revenue(company_id, limit)

        return {
            'top_by_quantity': top_by_quantity,
            'top_by_revenue': top_by_revenue,
            'limit': limit
        }
