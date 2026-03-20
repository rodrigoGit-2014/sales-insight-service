"""Celery tasks"""

from celery_app.tasks.process_transactions import process_transactions_task

__all__ = ["process_transactions_task"]
