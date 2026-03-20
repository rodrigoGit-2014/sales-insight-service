#!/bin/bash
# Database initialization script

set -e

echo "Initializing database..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U sales_user -d sales_db; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done

echo "PostgreSQL is up - executing database initialization"

# Run initialization SQL (already done by init.sql in docker-entrypoint-initdb.d)
echo "Database schema created successfully!"

# Verify tables
echo "Verifying tables..."
docker-compose exec -T postgres psql -U sales_user -d sales_db -c "\dt"

echo "Database initialization completed!"
