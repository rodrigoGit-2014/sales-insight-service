# Testing Guide - Sales Analytics API

Complete guide for testing the Sales Analytics API system.

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB of RAM available
- Ports 5432, 6379, 8000, 5555 available

## Step 1: Build and Start Services

```bash
# Navigate to project directory
cd /Users/rodrigocaceres/languages/python/analysis-basket

# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Check that all services are running
docker-compose ps
```

**Expected output:**
```
NAME                COMMAND                  SERVICE             STATUS              PORTS
sales_api           "uvicorn app.main:ap…"   api                 running             0.0.0.0:8000->8000/tcp
sales_flower        "celery -A celery_ap…"   flower              running             0.0.0.0:5555->5555/tcp
sales_postgres      "docker-entrypoint.s…"   postgres            running (healthy)   0.0.0.0:5432->5432/tcp
sales_redis         "docker-entrypoint.s…"   redis               running (healthy)   0.0.0.0:6379->6379/tcp
sales_worker        "celery -A celery_ap…"   worker              running
```

## Step 2: Verify Services

### 2.1 Check API Health

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "Sales Analytics API",
  "version": "1.0.0"
}
```

### 2.2 Check API Documentation

Open in browser: http://localhost:8000/docs

You should see the Swagger UI with all endpoints documented.

### 2.3 Check Flower Dashboard

Open in browser: http://localhost:5555

You should see the Celery task monitoring dashboard.

### 2.4 Verify Database

```bash
docker-compose exec postgres psql -U sales_user -d sales_db -c "\dt"
```

**Expected output:**
```
           List of relations
 Schema |  Name   | Type  |   Owner
--------+---------+-------+------------
 public | jobs    | table | sales_user
 public | tickets | table | sales_user
```

### 2.5 Check Logs

```bash
# API logs
docker-compose logs api | tail -20

# Worker logs
docker-compose logs worker | tail -20
```

All logs should show services running without errors.

## Step 3: Generate Sample Data

```bash
# Generate 10,000 rows (takes ~5 seconds)
python3 scripts/generate_sample_data.py --rows 10000 --output test_small.csv

# Or generate larger dataset for stress testing
python3 scripts/generate_sample_data.py --rows 100000 --output test_large.csv
```

**Expected output:**
```
Generating 10,000 rows of sample data...
Number of customers: 1,000
Generated 10000 rows...

Completed!
File: test_small.csv
Rows: 10,000
Size: 1.2 MB
```

## Step 4: Test Upload Endpoint

### 4.1 Upload Small File

```bash
curl -X POST "http://localhost:8000/api/v1/upload-transactions" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_small.csv" \
  | jq .
```

**Expected response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "File uploaded successfully. Processing has started.",
  "created_at": "2024-01-20T10:30:00Z"
}
```

**Save the job_id for next steps.**

### 4.2 Test Error Handling

```bash
# Test with invalid file type
echo "invalid" > test_invalid.txt
curl -X POST "http://localhost:8000/api/v1/upload-transactions" \
  -F "file=@test_invalid.txt"

# Expected: 400 Bad Request - Only CSV files are accepted
```

## Step 5: Monitor Job Processing

### 5.1 Check Job Status

```bash
# Replace {job_id} with actual job ID from Step 4
JOB_ID="550e8400-e29b-41d4-a716-446655440000"

# Poll job status (run multiple times)
curl "http://localhost:8000/api/v1/jobs/${JOB_ID}" | jq .
```

**Expected progression:**

Status: **pending**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "filename": "test_small.csv",
  "total_rows": null,
  "processed_rows": 0,
  "progress_percentage": null,
  ...
}
```

Status: **processing**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "filename": "test_small.csv",
  "total_rows": 10000,
  "processed_rows": 5000,
  "progress_percentage": 50.0,
  ...
}
```

Status: **completed**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "filename": "test_small.csv",
  "total_rows": 10000,
  "processed_rows": 10000,
  "progress_percentage": 100.0,
  "completed_at": "2024-01-20T10:31:23Z",
  ...
}
```

### 5.2 Monitor in Flower

Open http://localhost:5555/tasks

You should see the task `process_transactions` in progress or completed.

### 5.3 Check Worker Logs

```bash
docker-compose logs -f worker
```

You should see log messages like:
```
INFO Starting processing for job 550e8400-e29b-41d4-a716-446655440000
INFO Total rows to process: 10000
INFO Batch 1 inserted: 5000 records
INFO Batch 2 inserted: 5000 records
INFO Job 550e8400-e29b-41d4-a716-446655440000 completed successfully
```

## Step 6: Verify Data in Database

```bash
# Count total records
docker-compose exec postgres psql -U sales_user -d sales_db -c \
  "SELECT COUNT(*) FROM tickets;"

# Expected: 10000

# View sample data
docker-compose exec postgres psql -U sales_user -d sales_db -c \
  "SELECT id_pedido, id_cliente, fecha, nombre_producto, precio_total FROM tickets LIMIT 5;"

# Check job status in DB
docker-compose exec postgres psql -U sales_user -d sales_db -c \
  "SELECT id, status, filename, processed_rows, total_rows FROM jobs ORDER BY created_at DESC LIMIT 5;"
```

## Step 7: Test Analytics Endpoints

### 7.1 Total Sales

```bash
# All time total sales
curl "http://localhost:8000/api/v1/sales/total" | jq .

# Sales for specific date range
curl "http://localhost:8000/api/v1/sales/total?fecha_inicio=2024-01-01&fecha_fin=2024-12-31" | jq .
```

**Expected response:**
```json
{
  "fecha_inicio": "2024-01-01",
  "fecha_fin": "2024-12-31",
  "total_sales": 5678900.50,
  "total_orders": 10000,
  "average_order_value": 567.89
}
```

### 7.2 Monthly Trend

```bash
curl "http://localhost:8000/api/v1/sales/monthly-trend" | jq .
```

**Expected response:**
```json
{
  "data": [
    {
      "year": 2024,
      "month": 1,
      "total_sales": 450000.00,
      "order_count": 850,
      "avg_order_value": 529.41
    },
    {
      "year": 2024,
      "month": 2,
      "total_sales": 480000.00,
      "order_count": 900,
      "avg_order_value": 533.33
    },
    ...
  ]
}
```

### 7.3 Department Analytics

```bash
curl "http://localhost:8000/api/v1/analytics/departments" | jq .
```

**Expected response:**
```json
{
  "data": [
    {
      "id_departamento": "DEPT001",
      "total_sales": 1200000.00,
      "order_count": 2000,
      "percentage_of_total": 21.13
    },
    ...
  ]
}
```

### 7.4 Section Analytics

```bash
curl "http://localhost:8000/api/v1/analytics/sections" | jq .
```

### 7.5 Top Products by Quantity

```bash
curl "http://localhost:8000/api/v1/analytics/products/top-quantity?limit=10" | jq .
```

**Expected response:**
```json
{
  "data": [
    {
      "id_producto": "PROD001",
      "nombre_producto": "Laptop Dell XPS 15",
      "total_quantity": 1500,
      "total_revenue": 1950000.00,
      "order_count": 1500,
      "avg_unit_price": 1300.00
    },
    ...
  ],
  "limit": 10
}
```

### 7.6 Top Products by Revenue

```bash
curl "http://localhost:8000/api/v1/analytics/products/top-revenue?limit=10" | jq .
```

### 7.7 Top Customers

```bash
curl "http://localhost:8000/api/v1/analytics/customers/top?limit=20" | jq .
```

**Expected response:**
```json
{
  "data": [
    {
      "id_cliente": "CUST001",
      "total_spent": 25000.00,
      "order_count": 15,
      "average_order_value": 1666.67,
      "first_purchase": "2024-01-15",
      "last_purchase": "2024-12-28"
    },
    ...
  ],
  "limit": 20
}
```

### 7.8 Customer Average Spend

```bash
curl "http://localhost:8000/api/v1/analytics/customers/average-spend" | jq .
```

**Expected response:**
```json
{
  "average_spend_per_customer": 5678.90,
  "total_customers": 1000,
  "total_sales": 5678900.00
}
```

### 7.9 Order Statistics

```bash
curl "http://localhost:8000/api/v1/analytics/orders/count" | jq .
curl "http://localhost:8000/api/v1/analytics/orders/average-value" | jq .
```

## Step 8: Performance Testing

### 8.1 Test with Large File

```bash
# Generate 100k rows (~10MB)
python3 scripts/generate_sample_data.py --rows 100000 --output test_large.csv

# Upload and time it
time curl -X POST "http://localhost:8000/api/v1/upload-transactions" \
  -F "file=@test_large.csv" | jq .

# Expected: Should return in < 2 seconds regardless of file size
```

### 8.2 Monitor Memory Usage

```bash
# Watch memory usage during processing
docker stats

# Expected:
# - API: < 500MB
# - Worker: < 2GB (configured limit)
# - Postgres: Variable depending on data
# - Redis: < 100MB
```

### 8.3 Test Concurrent Uploads

```bash
# Upload multiple files simultaneously
for i in {1..3}; do
  curl -X POST "http://localhost:8000/api/v1/upload-transactions" \
    -F "file=@test_small.csv" &
done
wait

# All should succeed and return different job_ids
```

## Step 9: Error Handling Tests

### 9.1 Invalid CSV Structure

```bash
# Create CSV with missing columns
echo "invalid,headers" > test_invalid.csv
curl -X POST "http://localhost:8000/api/v1/upload-transactions" \
  -F "file=@test_invalid.csv"

# Expected: Job created but fails with validation error
```

### 9.2 Non-existent Job ID

```bash
curl "http://localhost:8000/api/v1/jobs/00000000-0000-0000-0000-000000000000"

# Expected: 404 Not Found
```

### 9.3 Invalid Query Parameters

```bash
# Invalid date range
curl "http://localhost:8000/api/v1/sales/total?fecha_inicio=2024-12-31&fecha_fin=2024-01-01"

# Expected: 400 Bad Request
```

## Step 10: Cleanup and Restart

```bash
# Stop all services
docker-compose down

# Clean up volumes (WARNING: deletes all data)
docker-compose down -v

# Restart fresh
docker-compose up -d
```

## Success Criteria Checklist

- [ ] All Docker containers start successfully
- [ ] Database schema created with all tables and indexes
- [ ] File upload returns job_id in < 1 second
- [ ] CSV with 10k rows processes in < 30 seconds
- [ ] CSV with 100k rows processes without OOM errors
- [ ] Job status updates correctly (pending → processing → completed)
- [ ] Data correctly inserted into database
- [ ] All 10 analytics endpoints return valid data
- [ ] Analytics queries respond in < 2 seconds
- [ ] Flower dashboard shows task execution
- [ ] API documentation accessible at /docs
- [ ] Error handling works correctly

## Performance Benchmarks

Expected performance on a modern system (4 CPU, 8GB RAM):

| Metric | Expected Value |
|--------|---------------|
| Upload response time | < 1 second |
| 10k rows processing | 10-30 seconds |
| 100k rows processing | 1-3 minutes |
| Analytics query time | < 2 seconds |
| API worker memory | < 500MB |
| Celery worker memory | < 2GB |

## Troubleshooting

### Issue: Services won't start

```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Worker not processing jobs

```bash
# Check worker is running
docker-compose ps worker

# Check Redis connection
docker-compose exec redis redis-cli ping

# Restart worker
docker-compose restart worker
```

### Issue: Database connection errors

```bash
# Check Postgres is healthy
docker-compose exec postgres pg_isready -U sales_user

# Verify database exists
docker-compose exec postgres psql -U sales_user -l
```

### Issue: Slow performance

```bash
# Check indexes exist
docker-compose exec postgres psql -U sales_user -d sales_db -c "\di"

# Analyze query performance
docker-compose exec postgres psql -U sales_user -d sales_db -c \
  "EXPLAIN ANALYZE SELECT * FROM tickets WHERE fecha = '2024-01-01';"
```

## Next Steps

After successful testing:

1. **Production Deployment**: Adjust `.env` for production settings
2. **Monitoring**: Set up Prometheus metrics and alerts
3. **Security**: Add authentication (JWT) and rate limiting
4. **Scaling**: Configure horizontal scaling for API and workers
5. **Backups**: Set up automated database backups

## Support

For issues or questions:
- Check logs: `docker-compose logs [service_name]`
- Review documentation: `README.md`
- Verify configuration: `.env`
