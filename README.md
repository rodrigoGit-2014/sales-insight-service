# Sales Analytics API

Production-ready FastAPI backend for sales analytics with asynchronous CSV processing.

## Features

- **Asynchronous CSV Processing**: Handle large files (up to 500MB) without blocking
- **Celery + Redis**: Background task processing with progress tracking
- **PostgreSQL**: Optimized database with indexes for analytics queries
- **FastAPI**: Modern, fast web framework with automatic OpenAPI docs
- **Docker Compose**: Complete containerized setup
- **Production-Ready**: Error handling, logging, validation, and monitoring

## Architecture

```
├── FastAPI API (Port 8000)
├── Celery Worker (Background processing)
├── PostgreSQL 15 (Database)
├── Redis 7 (Message broker)
└── Flower (Celery monitoring - Port 5555)
```

## Quick Start

### 1. Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)

### 2. Setup

```bash
# Clone the repository
cd analysis-basket

# Copy environment variables
cp .env.example .env

# Build and start services
make build
make up

# Or using docker-compose directly
docker-compose build
docker-compose up -d
```

### 3. Verify Services

```bash
# Check all services are running
docker-compose ps

# Expected output:
# sales_api       Running   0.0.0.0:8000->8000/tcp
# sales_worker    Running
# sales_postgres  Running   0.0.0.0:5432->5432/tcp
# sales_redis     Running   0.0.0.0:6379->6379/tcp
# sales_flower    Running   0.0.0.0:5555->5555/tcp
```

### 4. Access Services

- **API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Flower (Celery Monitoring)**: http://localhost:5555

## Usage

### Generate Sample Data

```bash
# Generate 10,000 rows
make generate-data

# Or with custom parameters
python3 scripts/generate_sample_data.py --rows 100000 --customers 5000 --output large_sample.csv
```

### Upload CSV File

```bash
# Using curl
curl -X POST "http://localhost:8000/api/v1/upload-transactions" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_transactions.csv"

# Response:
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "File uploaded successfully. Processing has started.",
  "created_at": "2024-01-20T10:30:00Z"
}
```

### Check Job Status

```bash
# Replace {job_id} with the actual job ID
curl "http://localhost:8000/api/v1/jobs/{job_id}"

# Response:
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "filename": "sample_transactions.csv",
  "total_rows": 10000,
  "processed_rows": 5000,
  "progress_percentage": 50.0,
  "error_message": null,
  "created_at": "2024-01-20T10:30:00Z",
  "started_at": "2024-01-20T10:30:05Z",
  "completed_at": null
}
```

### Query Analytics

```bash
# Get total sales
curl "http://localhost:8000/api/v1/sales/total?fecha_inicio=2024-01-01&fecha_fin=2024-12-31"

# Get monthly trend
curl "http://localhost:8000/api/v1/sales/monthly-trend"

# Get top products by quantity
curl "http://localhost:8000/api/v1/analytics/products/top-quantity?limit=10"

# Get top customers
curl "http://localhost:8000/api/v1/analytics/customers/top?limit=20"

# Get department analytics
curl "http://localhost:8000/api/v1/analytics/departments"
```

## API Endpoints

### Upload & Jobs

- `POST /api/v1/upload-transactions` - Upload CSV file
- `GET /api/v1/jobs/{job_id}` - Get job status

### Sales

- `GET /api/v1/sales/total` - Total sales (with date filters)
- `GET /api/v1/sales/monthly-trend` - Monthly sales trend

### Analytics

- `GET /api/v1/analytics/departments` - Department analytics
- `GET /api/v1/analytics/sections` - Section analytics
- `GET /api/v1/analytics/products/top-quantity` - Top products by quantity
- `GET /api/v1/analytics/products/top-revenue` - Top products by revenue
- `GET /api/v1/analytics/customers/top` - Top customers
- `GET /api/v1/analytics/customers/average-spend` - Average customer spend
- `GET /api/v1/analytics/orders/count` - Order count
- `GET /api/v1/analytics/orders/average-value` - Average order value

## CSV File Format

Required columns:

```csv
id_pedido,id_cliente,fecha,hora,id_departamento,id_seccion,id_producto,nombre_producto,precio_unitario,cantidad,precio_total
ORD00001,CUST001,2024-01-15,14,DEPT001,SEC001,PROD001,Laptop Dell XPS,1299.99,1,1299.99
```

## Development

### View Logs

```bash
# All services
make logs

# Specific service
make logs-api
make logs-worker

# Or with docker-compose
docker-compose logs -f api
docker-compose logs -f worker
```

### Access Database

```bash
# PostgreSQL shell
make shell-db

# Or directly
docker-compose exec postgres psql -U sales_user -d sales_db

# Useful queries
SELECT COUNT(*) FROM tickets;
SELECT * FROM jobs ORDER BY created_at DESC LIMIT 5;
```

### Access API Container

```bash
make shell-api

# Or directly
docker-compose exec api /bin/bash
```

## Configuration

Edit `.env` file to customize:

```env
# Database
POSTGRES_USER=sales_user
POSTGRES_PASSWORD=sales_password
POSTGRES_DB=sales_db

# Redis
REDIS_URL=redis://redis:6379/0

# Application
MAX_UPLOAD_SIZE=524288000  # 500MB
LOG_LEVEL=INFO
```

## Performance

### Database Indexes

The following indexes are created for optimal query performance:

- `idx_tickets_fecha` - Date queries
- `idx_tickets_id_cliente` - Customer queries
- `idx_tickets_id_producto` - Product queries
- `idx_tickets_id_departamento` - Department queries
- `idx_tickets_id_seccion` - Section queries

### Memory Usage

- **API**: ~200-500MB per worker
- **Celery Worker**: ~512MB-2GB (configured limit)
- **PostgreSQL**: ~256MB base + data
- **Redis**: ~50-512MB

### Scalability

To scale horizontally:

```bash
# Scale API workers
docker-compose up -d --scale api=3

# Scale Celery workers
docker-compose up -d --scale worker=3
```

## Monitoring

### Flower Dashboard

Access http://localhost:5555 to monitor:
- Active tasks
- Task history
- Worker status
- Task statistics

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/readiness
```

## Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Rebuild images
make clean
make build
make up
```

### Database connection errors

```bash
# Verify PostgreSQL is running
docker-compose exec postgres pg_isready -U sales_user

# Check database exists
docker-compose exec postgres psql -U sales_user -l
```

### Worker not processing jobs

```bash
# Check worker logs
make logs-worker

# Check Redis connection
docker-compose exec redis redis-cli ping

# Restart worker
docker-compose restart worker
```

## Project Structure

```
analysis-basket/
├── app/
│   ├── api/v1/endpoints/      # API endpoints
│   ├── core/                  # Config, logging, exceptions
│   ├── db/                    # Database session
│   ├── models/                # SQLAlchemy models
│   ├── repositories/          # Data access layer
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   ├── utils/                 # Utilities
│   └── main.py                # FastAPI app
├── celery_app/
│   ├── tasks/                 # Celery tasks
│   └── celery.py              # Celery config
├── docker/
│   ├── api.Dockerfile
│   ├── worker.Dockerfile
│   └── postgres/init.sql
├── scripts/
│   ├── generate_sample_data.py
│   └── init_db.sh
├── docker-compose.yml
├── requirements.txt
├── Makefile
└── README.md
```

## Technologies

- **FastAPI 0.109+** - Web framework
- **PostgreSQL 15** - Database
- **Redis 7** - Message broker
- **Celery 5.3** - Task queue
- **SQLAlchemy 2.0** - ORM
- **Pydantic 2.0** - Data validation
- **Docker & Docker Compose** - Containerization

## License

MIT License

## Support

For issues or questions, please open an issue on GitHub or contact the development team.
