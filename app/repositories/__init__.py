"""Repository layer for data access"""

from app.repositories.ticket_repository import TicketRepository
from app.repositories.job_repository import JobRepository

__all__ = ["TicketRepository", "JobRepository"]
