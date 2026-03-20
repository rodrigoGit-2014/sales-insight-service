"""Service for analytics calculations"""

from typing import Dict, List, Any
from decimal import Decimal
from sqlalchemy.orm import Session

from app.repositories.ticket_repository import TicketRepository


class AnalyticsService:
    """Service for analytics-related business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.ticket_repository = TicketRepository(db)

    def get_department_analytics(self) -> List[Dict[str, Any]]:
        """
        Get analytics grouped by department.

        Returns:
            List of department analytics data
        """
        return self.ticket_repository.get_department_analytics()

    def get_section_analytics(self) -> List[Dict[str, Any]]:
        """
        Get analytics grouped by section.

        Returns:
            List of section analytics data
        """
        return self.ticket_repository.get_section_analytics()

    def get_top_products_by_quantity(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get top products by quantity sold.

        Args:
            limit: Number of top products to return

        Returns:
            Dictionary with product data and limit
        """
        products = self.ticket_repository.get_top_products_by_quantity(limit)
        return {
            'data': products,
            'limit': limit
        }

    def get_top_products_by_revenue(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get top products by revenue.

        Args:
            limit: Number of top products to return

        Returns:
            Dictionary with product data and limit
        """
        products = self.ticket_repository.get_top_products_by_revenue(limit)
        return {
            'data': products,
            'limit': limit
        }

    def get_top_customers(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get top customers by total spend.

        Args:
            limit: Number of top customers to return

        Returns:
            Dictionary with customer data and limit
        """
        customers = self.ticket_repository.get_top_customers(limit)
        return {
            'data': customers,
            'limit': limit
        }

    def get_customer_average_spend(self) -> Dict[str, Any]:
        """
        Get average spend per customer.

        Returns:
            Dictionary with average spend statistics
        """
        return self.ticket_repository.get_customer_average_spend()

    def get_order_statistics(self) -> Dict[str, Any]:
        """
        Get overall order statistics.

        Returns:
            Dictionary with order count, average value, and total sales
        """
        order_count = self.ticket_repository.get_order_count()
        avg_order_value = self.ticket_repository.get_average_order_value()
        total_sales = order_count * avg_order_value if order_count > 0 else Decimal('0')

        return {
            'total_orders': order_count,
            'average_order_value': avg_order_value,
            'total_sales': total_sales
        }

    def get_product_performance_summary(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get comprehensive product performance summary.

        Args:
            limit: Number of top products to include

        Returns:
            Dictionary with top products by quantity and revenue
        """
        top_by_quantity = self.ticket_repository.get_top_products_by_quantity(limit)
        top_by_revenue = self.ticket_repository.get_top_products_by_revenue(limit)

        return {
            'top_by_quantity': top_by_quantity,
            'top_by_revenue': top_by_revenue,
            'limit': limit
        }
