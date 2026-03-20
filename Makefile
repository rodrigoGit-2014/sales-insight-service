.PHONY: help build up down restart logs shell test clean generate-data

help:
	@echo "Available commands:"
	@echo "  make build         - Build Docker images"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo "  make restart       - Restart all services"
	@echo "  make logs          - View logs (all services)"
	@echo "  make logs-api      - View API logs"
	@echo "  make logs-worker   - View worker logs"
	@echo "  make shell-api     - Open shell in API container"
	@echo "  make shell-db      - Open PostgreSQL shell"
	@echo "  make generate-data - Generate sample CSV data"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean up containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "API: http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"
	@echo "Flower: http://localhost:5555"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f worker

shell-api:
	docker-compose exec api /bin/bash

shell-db:
	docker-compose exec postgres psql -U sales_user -d sales_db

generate-data:
	python3 scripts/generate_sample_data.py --rows 10000 --output sample_transactions.csv

test:
	docker-compose exec api pytest tests/ -v

clean:
	docker-compose down -v
	rm -f sample_transactions.csv
	rm -rf uploads/*.csv
	@echo "Cleanup completed!"
