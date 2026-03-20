"""Repository for Ticket model with complex analytical queries"""

from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal
from sqlalchemy import func, desc, and_
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.repositories.base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    """Repository for Ticket model with analytical query methods"""

    def __init__(self, db: Session):
        super().__init__(Ticket, db)

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
            Dictionary with total_sales, total_orders, average_order_value
        """
        query = self.db.query(
            func.sum(Ticket.precio_total).label('total_sales'),
            func.count(func.distinct(Ticket.id_pedido)).label('total_orders')
        )

        if fecha_inicio:
            query = query.filter(Ticket.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Ticket.fecha <= fecha_fin)

        result = query.first()

        total_sales = result.total_sales or Decimal('0')
        total_orders = result.total_orders or 0
        avg_order_value = (total_sales / total_orders) if total_orders > 0 else Decimal('0')

        return {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'average_order_value': avg_order_value
        }

    def get_monthly_trend(self) -> List[Dict[str, Any]]:
        """
        Get monthly sales trend.

        Returns:
            List of dictionaries with year, month, total_sales, order_count, avg_order_value
        """
        results = self.db.query(
            func.extract('year', Ticket.fecha).label('year'),
            func.extract('month', Ticket.fecha).label('month'),
            func.sum(Ticket.precio_total).label('total_sales'),
            func.count(func.distinct(Ticket.id_pedido)).label('order_count')
        ).group_by(
            func.extract('year', Ticket.fecha),
            func.extract('month', Ticket.fecha)
        ).order_by('year', 'month').all()

        return [
            {
                'year': int(row.year),
                'month': int(row.month),
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

    def get_department_analytics(self) -> List[Dict[str, Any]]:
        """
        Get sales analytics by department.

        Returns:
            List of dictionaries with department data
        """
        # Get total sales for percentage calculation
        total_sales = self.db.query(func.sum(Ticket.precio_total)).scalar() or Decimal('0')

        results = self.db.query(
            Ticket.id_departamento,
            func.sum(Ticket.precio_total).label('total_sales'),
            func.count(func.distinct(Ticket.id_pedido)).label('order_count')
        ).group_by(
            Ticket.id_departamento
        ).order_by(
            desc('total_sales')
        ).all()

        return [
            {
                'id_departamento': row.id_departamento,
                'total_sales': row.total_sales or Decimal('0'),
                'order_count': row.order_count or 0,
                'percentage_of_total': (
                    round((row.total_sales / total_sales) * 100, 2)
                    if total_sales > 0
                    else Decimal('0')
                )
            }
            for row in results
        ]

    def get_section_analytics(self) -> List[Dict[str, Any]]:
        """
        Get sales analytics by section.

        Returns:
            List of dictionaries with section data
        """
        total_sales = self.db.query(func.sum(Ticket.precio_total)).scalar() or Decimal('0')

        results = self.db.query(
            Ticket.id_seccion,
            Ticket.id_departamento,
            func.sum(Ticket.precio_total).label('total_sales'),
            func.count(func.distinct(Ticket.id_pedido)).label('order_count')
        ).group_by(
            Ticket.id_seccion,
            Ticket.id_departamento
        ).order_by(
            desc('total_sales')
        ).all()

        return [
            {
                'id_seccion': row.id_seccion,
                'id_departamento': row.id_departamento,
                'total_sales': row.total_sales or Decimal('0'),
                'order_count': row.order_count or 0,
                'percentage_of_total': (
                    round((row.total_sales / total_sales) * 100, 2)
                    if total_sales > 0
                    else Decimal('0')
                )
            }
            for row in results
        ]

    def get_top_products_by_quantity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top products by quantity sold.

        Args:
            limit: Number of top products to return

        Returns:
            List of dictionaries with product data
        """
        results = self.db.query(
            Ticket.id_producto,
            Ticket.nombre_producto,
            func.sum(Ticket.cantidad).label('total_quantity'),
            func.sum(Ticket.precio_total).label('total_revenue'),
            func.count(func.distinct(Ticket.id_pedido)).label('order_count'),
            func.avg(Ticket.precio_unitario).label('avg_unit_price')
        ).group_by(
            Ticket.id_producto,
            Ticket.nombre_producto
        ).order_by(
            desc('total_quantity')
        ).limit(limit).all()

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

    def get_top_products_by_revenue(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top products by revenue.

        Args:
            limit: Number of top products to return

        Returns:
            List of dictionaries with product data
        """
        results = self.db.query(
            Ticket.id_producto,
            Ticket.nombre_producto,
            func.sum(Ticket.cantidad).label('total_quantity'),
            func.sum(Ticket.precio_total).label('total_revenue'),
            func.count(func.distinct(Ticket.id_pedido)).label('order_count'),
            func.avg(Ticket.precio_unitario).label('avg_unit_price')
        ).group_by(
            Ticket.id_producto,
            Ticket.nombre_producto
        ).order_by(
            desc('total_revenue')
        ).limit(limit).all()

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

    def get_top_customers(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get top customers by total spend.

        Args:
            limit: Number of top customers to return

        Returns:
            List of dictionaries with customer data
        """
        results = self.db.query(
            Ticket.id_cliente,
            func.sum(Ticket.precio_total).label('total_spent'),
            func.count(func.distinct(Ticket.id_pedido)).label('order_count'),
            func.min(Ticket.fecha).label('first_purchase'),
            func.max(Ticket.fecha).label('last_purchase')
        ).group_by(
            Ticket.id_cliente
        ).order_by(
            desc('total_spent')
        ).limit(limit).all()

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

    def get_customer_average_spend(self) -> Dict[str, Any]:
        """
        Calculate average spend per customer.

        Returns:
            Dictionary with average_spend_per_customer, total_customers, total_sales
        """
        result = self.db.query(
            func.count(func.distinct(Ticket.id_cliente)).label('total_customers'),
            func.sum(Ticket.precio_total).label('total_sales')
        ).first()

        total_customers = result.total_customers or 0
        total_sales = result.total_sales or Decimal('0')
        avg_spend = (total_sales / total_customers) if total_customers > 0 else Decimal('0')

        return {
            'average_spend_per_customer': avg_spend,
            'total_customers': total_customers,
            'total_sales': total_sales
        }

    def get_order_count(self) -> int:
        """
        Get total number of orders.

        Returns:
            Total order count
        """
        return self.db.query(func.count(func.distinct(Ticket.id_pedido))).scalar() or 0

    def get_average_order_value(self) -> Decimal:
        """
        Calculate average order value.

        Returns:
            Average order value
        """
        result = self.db.query(
            func.sum(Ticket.precio_total).label('total_sales'),
            func.count(func.distinct(Ticket.id_pedido)).label('total_orders')
        ).first()

        total_sales = result.total_sales or Decimal('0')
        total_orders = result.total_orders or 0

        return (total_sales / total_orders) if total_orders > 0 else Decimal('0')
