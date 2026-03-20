"""Celery application configuration"""

from celery import Celery
import os
from kombu import Exchange, Queue

# Get configuration from environment
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Create Celery instance
celery_app = Celery('sales_analytics')

# Configure Celery
celery_app.conf.update(
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # Only fetch one task at a time
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (prevent memory leaks)
    task_acks_late=True,  # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Reject tasks if worker dies
    result_expires=3600,  # Results expire after 1 hour

    # Task routes
    task_routes={
        'celery_app.tasks.process_transactions.process_transactions_task': {
            'queue': 'default',
            'routing_key': 'default',
        }
    },

    # Queues
    task_queues=(
        Queue('default', Exchange('default'), routing_key='default'),
    ),

    # Retry configuration
    task_annotations={
        'celery_app.tasks.process_transactions.process_transactions_task': {
            'rate_limit': '10/m',  # Max 10 tasks per minute
        }
    }
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['celery_app.tasks'])

if __name__ == '__main__':
    celery_app.start()
