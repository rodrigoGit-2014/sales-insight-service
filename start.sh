#!/bin/bash
# Start script for Railway that runs both web and worker processes

# Start Celery worker in background
celery -A celery_app.celery worker --loglevel=info --concurrency=2 &

# Start web server in foreground
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
