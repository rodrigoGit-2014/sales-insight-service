"""Repository for Ticket model with complex analytical queries"""

from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal
from sqlalchemy import func, desc, and_, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session
import logging

from app.models.ticket import Ticket
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class TicketRepository(BaseRepository[Ticket]):
    """Repository for Ticket model with analytical query methods"""

    def __init__(self, db: Session):
        super().__init__(Ticket, db)
        self._views_verified = False

    def _ensure_materialized_views(self):
        """Create materialized views if they don't exist. Called once per repository instance."""
        if self._views_verified:
            return
        try:
            result = self.db.execute(text("""
                SELECT COUNT(*) FROM pg_matviews
                WHERE schemaname = 'public'
                AND matviewname IN (
                    'mv_daily_sales', 'mv_monthly_trend',
                    'mv_department_analytics', 'mv_section_analytics',
                    'mv_product_analytics', 'mv_customer_top'
                )
            """))
            if result.scalar() == 6:
                self._views_verified = True
                return
            logger.warning("Missing materialized views detected, creating them...")
            from app.db.session import create_materialized_views
            create_materialized_views()
            self._views_verified = True
        except Exception as e:
            logger.error(f"Failed to ensure materialized views: {e}")

    def get_total_sales(
        self,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate total sales for a date range.

        Args:
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            Dictionary with total_sales, total_orders, total_clients, average_order_value
        """
        self._ensure_materialized_views()
        params = {}
        where_clauses = []

        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
            where_clauses.append("fecha >= :fecha_inicio")
        if fecha_fin:
            params['fecha_fin'] = fecha_fin
            where_clauses.append("fecha <= :fecha_fin")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        result = self.db.execute(
            text(f"""
                SELECT
                    COALESCE(SUM(total_sales), 0) AS total_sales,
                    COALESCE(SUM(order_count), 0) AS total_orders,
                    COALESCE(SUM(client_count), 0) AS total_clients,
                    CASE WHEN SUM(total_rows) > 0
                         THEN SUM(total_sales) / SUM(total_rows)
                         ELSE 0 END AS average_order_value
                FROM mv_daily_sales
                {where_sql}
            """),
            params
        ).first()

        return {
            'total_sales': Decimal(str(result.total_sales)),
            'total_orders': int(result.total_orders),
            'total_clients': int(result.total_clients),
            'average_order_value': Decimal(str(result.average_order_value))
        }

    def get_monthly_trend(
        self,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get monthly sales trend.
        Uses mv_monthly_trend materialized view for performance.

        Args:
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            List of dictionaries with year, month, total_sales, order_count, avg_order_value
        """
        self._ensure_materialized_views()
        where_sql, params = self._monthly_trend_filter(fecha_inicio, fecha_fin)

        results = self.db.execute(
            text(f"""
                SELECT year, month, total_sales, order_count
                FROM mv_monthly_trend
                {where_sql}
                ORDER BY year, month
            """),
            params
        ).fetchall()

        return [
            {
                'year': row.year,
                'month': row.month,
                'total_sales': row.total_sales or Decimal('0'),
                'order_count': row.order_count or 0,
                'avg_order_value': (
                    (row.total_sales / row.order_count)
                    if row.order_count > 0
                    else Decimal('0')
                )
            }
            for row in results
        ]

    def get_department_analytics(
        self,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get sales analytics by department.
        Uses mv_department_analytics materialized view for performance.

        Args:
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            List of dictionaries with department data
        """
        self._ensure_materialized_views()
        params = {}
        where_clauses = []

        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
            where_clauses.append("fecha >= :fecha_inicio")
        if fecha_fin:
            params['fecha_fin'] = fecha_fin
            where_clauses.append("fecha <= :fecha_fin")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        results = self.db.execute(
            text(f"""
                WITH dept_data AS (
                    SELECT id_departamento,
                           SUM(total_sales) AS total_sales,
                           SUM(order_count) AS order_count
                    FROM mv_department_analytics
                    {where_sql}
                    GROUP BY id_departamento
                ),
                grand_total AS (
                    SELECT COALESCE(SUM(total_sales), 0) AS grand_total FROM dept_data
                )
                SELECT d.id_departamento, d.total_sales, d.order_count,
                       CASE WHEN g.grand_total > 0
                            THEN ROUND((d.total_sales / g.grand_total) * 100, 2)
                            ELSE 0 END AS percentage_of_total
                FROM dept_data d, grand_total g
                ORDER BY d.total_sales DESC
            """),
            params
        ).fetchall()

        return [
            {
                'id_departamento': row.id_departamento,
                'total_sales': row.total_sales or Decimal('0'),
                'order_count': row.order_count or 0,
                'percentage_of_total': row.percentage_of_total or Decimal('0')
            }
            for row in results
        ]

    def get_section_analytics(
        self,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get sales analytics by section.
        Uses mv_section_analytics materialized view for performance.

        Args:
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            List of dictionaries with section data
        """
        self._ensure_materialized_views()
        params = {}
        where_clauses = []

        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
            where_clauses.append("fecha >= :fecha_inicio")
        if fecha_fin:
            params['fecha_fin'] = fecha_fin
            where_clauses.append("fecha <= :fecha_fin")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        results = self.db.execute(
            text(f"""
                WITH section_data AS (
                    SELECT id_seccion, id_departamento,
                           SUM(total_sales) AS total_sales,
                           SUM(order_count) AS order_count
                    FROM mv_section_analytics
                    {where_sql}
                    GROUP BY id_seccion, id_departamento
                ),
                grand_total AS (
                    SELECT COALESCE(SUM(total_sales), 0) AS grand_total FROM section_data
                )
                SELECT s.id_seccion, s.id_departamento, s.total_sales, s.order_count,
                       CASE WHEN g.grand_total > 0
                            THEN ROUND((s.total_sales / g.grand_total) * 100, 2)
                            ELSE 0 END AS percentage_of_total
                FROM section_data s, grand_total g
                ORDER BY s.total_sales DESC
            """),
            params
        ).fetchall()

        return [
            {
                'id_seccion': row.id_seccion,
                'id_departamento': row.id_departamento,
                'total_sales': row.total_sales or Decimal('0'),
                'order_count': row.order_count or 0,
                'percentage_of_total': row.percentage_of_total or Decimal('0')
            }
            for row in results
        ]

    def get_top_products_by_quantity(
        self,
        limit: int = 10,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top products by quantity sold.
        Uses mv_product_analytics materialized view for performance.

        Args:
            limit: Number of top products to return
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            List of dictionaries with product data
        """
        self._ensure_materialized_views()
        params = {"limit": limit}
        where_clauses = []

        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
            where_clauses.append("fecha >= :fecha_inicio")
        if fecha_fin:
            params['fecha_fin'] = fecha_fin
            where_clauses.append("fecha <= :fecha_fin")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        results = self.db.execute(
            text(f"""
                SELECT id_producto, nombre_producto,
                       SUM(total_quantity) AS total_quantity,
                       SUM(total_revenue) AS total_revenue,
                       SUM(order_count) AS order_count,
                       AVG(avg_unit_price) AS avg_unit_price
                FROM mv_product_analytics
                {where_sql}
                GROUP BY id_producto, nombre_producto
                ORDER BY total_quantity DESC
                LIMIT :limit
            """),
            params
        ).fetchall()

        return [
            {
                'id_producto': row.id_producto,
                'nombre_producto': row.nombre_producto,
                'total_quantity': row.total_quantity or 0,
                'total_revenue': row.total_revenue or Decimal('0'),
                'order_count': row.order_count or 0,
                'avg_unit_price': row.avg_unit_price or Decimal('0')
            }
            for row in results
        ]

    def get_top_products_by_revenue(
        self,
        limit: int = 10,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top products by revenue.
        Uses mv_product_analytics materialized view for performance.

        Args:
            limit: Number of top products to return
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            List of dictionaries with product data
        """
        self._ensure_materialized_views()
        params = {"limit": limit}
        where_clauses = []

        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
            where_clauses.append("fecha >= :fecha_inicio")
        if fecha_fin:
            params['fecha_fin'] = fecha_fin
            where_clauses.append("fecha <= :fecha_fin")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        results = self.db.execute(
            text(f"""
                SELECT id_producto, nombre_producto,
                       SUM(total_quantity) AS total_quantity,
                       SUM(total_revenue) AS total_revenue,
                       SUM(order_count) AS order_count,
                       AVG(avg_unit_price) AS avg_unit_price
                FROM mv_product_analytics
                {where_sql}
                GROUP BY id_producto, nombre_producto
                ORDER BY total_revenue DESC
                LIMIT :limit
            """),
            params
        ).fetchall()

        return [
            {
                'id_producto': row.id_producto,
                'nombre_producto': row.nombre_producto,
                'total_quantity': row.total_quantity or 0,
                'total_revenue': row.total_revenue or Decimal('0'),
                'order_count': row.order_count or 0,
                'avg_unit_price': row.avg_unit_price or Decimal('0')
            }
            for row in results
        ]

    def get_top_customers(
        self,
        limit: int = 20,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top customers by total spend.
        Uses mv_customer_top materialized view for performance.

        Args:
            limit: Number of top customers to return
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            List of dictionaries with customer data
        """
        self._ensure_materialized_views()
        params = {"limit": limit}
        where_clauses = []

        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
            where_clauses.append("fecha >= :fecha_inicio")
        if fecha_fin:
            params['fecha_fin'] = fecha_fin
            where_clauses.append("fecha <= :fecha_fin")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        results = self.db.execute(
            text(f"""
                SELECT id_cliente,
                       SUM(total_spent) AS total_spent,
                       SUM(order_count) AS order_count,
                       MIN(fecha) AS first_purchase,
                       MAX(fecha) AS last_purchase
                FROM mv_customer_top
                {where_sql}
                GROUP BY id_cliente
                ORDER BY total_spent DESC
                LIMIT :limit
            """),
            params
        ).fetchall()

        return [
            {
                'id_cliente': row.id_cliente,
                'total_spent': row.total_spent or Decimal('0'),
                'order_count': row.order_count or 0,
                'average_order_value': (
                    (row.total_spent / row.order_count)
                    if row.order_count > 0
                    else Decimal('0')
                ),
                'first_purchase': row.first_purchase,
                'last_purchase': row.last_purchase
            }
            for row in results
        ]

    def get_customer_average_spend(
        self,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate average spend per customer.
        Uses mv_daily_sales materialized view for performance.

        Args:
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            Dictionary with average_spend_per_customer, total_customers, total_sales
        """
        self._ensure_materialized_views()
        params = {}
        where_clauses = []

        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio
            where_clauses.append("fecha >= :fecha_inicio")
        if fecha_fin:
            params['fecha_fin'] = fecha_fin
            where_clauses.append("fecha <= :fecha_fin")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        result = self.db.execute(
            text(f"""
                SELECT COALESCE(SUM(client_count), 0) AS total_customers,
                       COALESCE(SUM(total_sales), 0) AS total_sales
                FROM mv_daily_sales
                {where_sql}
            """),
            params
        ).first()

        total_customers = int(result.total_customers)
        total_sales = Decimal(str(result.total_sales))
        avg_spend = (total_sales / total_customers) if total_customers > 0 else Decimal('0')

        return {
            'average_spend_per_customer': avg_spend,
            'total_customers': total_customers,
            'total_sales': total_sales
        }

    def _monthly_trend_filter(self, fecha_inicio=None, fecha_fin=None):
        """Build WHERE clause for mv_monthly_trend based on date range."""
        params = {}
        where_clauses = []
        if fecha_inicio:
            params['start_year'] = fecha_inicio.year
            params['start_month'] = fecha_inicio.month
            where_clauses.append("(year > :start_year OR (year = :start_year AND month >= :start_month))")
        if fecha_fin:
            params['end_year'] = fecha_fin.year
            params['end_month'] = fecha_fin.month
            where_clauses.append("(year < :end_year OR (year = :end_year AND month <= :end_month))")
        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        return where_sql, params

    def get_order_count(
        self,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> int:
        """
        Get total number of orders.
        Uses mv_monthly_trend materialized view for performance.

        Args:
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            Total order count
        """
        self._ensure_materialized_views()
        where_sql, params = self._monthly_trend_filter(fecha_inicio, fecha_fin)
        result = self.db.execute(
            text(f"SELECT COALESCE(SUM(order_count), 0) AS total FROM mv_monthly_trend {where_sql}"),
            params
        ).first()
        return int(result.total)

    def get_average_order_value(
        self,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Decimal:
        """
        Calculate average order value.
        Uses mv_monthly_trend materialized view for performance.

        Args:
            fecha_inicio: Start date (inclusive)
            fecha_fin: End date (inclusive)

        Returns:
            Average order value
        """
        self._ensure_materialized_views()
        where_sql, params = self._monthly_trend_filter(fecha_inicio, fecha_fin)
        result = self.db.execute(
            text(f"""
                SELECT COALESCE(SUM(total_sales), 0) AS total_sales,
                       COALESCE(SUM(order_count), 0) AS total_orders
                FROM mv_monthly_trend {where_sql}
            """),
            params
        ).first()

        total_sales = Decimal(str(result.total_sales))
        total_orders = int(result.total_orders)

        return (total_sales / total_orders) if total_orders > 0 else Decimal('0')
