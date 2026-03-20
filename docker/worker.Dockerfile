FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Flower for monitoring
RUN pip install --no-cache-dir flower==2.0.1

# Copy application code
COPY app /app/app
COPY celery_app /app/celery_app

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV C_FORCE_ROOT=true

CMD ["celery", "-A", "celery_app.celery", "worker", "--loglevel=info"]
