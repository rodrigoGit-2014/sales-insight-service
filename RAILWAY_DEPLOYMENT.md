# Railway Deployment Guide

## Problem Diagnosis

Your async processing wasn't working because Railway only runs ONE process per service. Your Procfile defined both `web` and `worker` processes, but Railway was only executing the `web` process, leaving no Celery worker to consume tasks from Redis.

## Solution Implemented

I've updated the project to run both the web server and Celery worker in a single process using a startup script (`start.sh`).

### Changes Made:

1. **Created `start.sh`**: Starts both Celery worker (background) and web server (foreground)
2. **Updated `Procfile`**: Now uses `./start.sh` instead of separate processes
3. **Updated `Dockerfile`**: Copies and makes the start script executable
4. **Added `/celery-health` endpoint**: Verify Celery workers are running

## Deployment Steps

### 1. Push Changes to Git

```bash
git add .
git commit -m "Fix Railway Celery worker deployment"
git push
```

### 2. Configure Railway Environment Variables

Make sure these are set in your Railway service:

```bash
# Database
DATABASE_URL=<your-postgres-url>

# Redis/Celery
CELERY_BROKER_URL=redis://default:GuAUSOEzWqDTwvLTNoIfNpqkjyYauHbW@redis.railway.internal:6379
CELERY_RESULT_BACKEND=redis://default:GuAUSOEzWqDTwvLTNoIfNpqkjyYauHbW@redis.railway.internal:6379

# Application
PORT=8000
UPLOAD_DIR=/app/uploads
```

### 3. Verify Deployment

After deployment, check these endpoints:

1. **Health Check**:
   ```bash
   curl https://your-app.railway.app/health
   ```

2. **Celery Health Check** (IMPORTANT):
   ```bash
   curl https://your-app.railway.app/celery-health
   ```

   Expected response when working:
   ```json
   {
     "status": "healthy",
     "active_workers": 1,
     "workers": ["celery@<worker-id>"],
     "registered_tasks": ["process_transactions"],
     "broker_url": "redis.railway.internal:6379"
   }
   ```

3. **Test Upload**:
   ```bash
   curl -X POST https://your-app.railway.app/api/v1/upload-transactions \
     -F "file=@test.csv"
   ```

### 4. Check Logs

Monitor Railway logs to verify both processes are running:

```
[INFO] Starting Celery worker...
[INFO] celery@<worker-id> ready
[INFO] Starting Uvicorn server...
[INFO] Application startup complete
```

## Alternative: Two-Service Deployment (More Scalable)

If you need to scale workers independently, create TWO Railway services:

### Service 1: Web API
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- **Environment Variables**: All variables including Redis URL

### Service 2: Celery Worker
- **Start Command**: `celery -A celery_app.celery worker --loglevel=info --concurrency=2`
- **Environment Variables**: Same as Service 1 (especially `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `DATABASE_URL`)

Benefits:
- Scale workers independently
- Restart workers without affecting web traffic
- Better separation of concerns

## Troubleshooting

### Issue: `/celery-health` shows "No Celery workers are running"

**Cause**: Worker process didn't start or crashed

**Solutions**:
1. Check Railway logs for worker startup errors
2. Verify Redis is accessible: `redis://redis.railway.internal:6379`
3. Ensure `start.sh` has execute permissions (should be automatic)

### Issue: Tasks stuck in "PENDING" status

**Cause**: Worker not consuming from queue

**Solutions**:
1. Check `/celery-health` endpoint
2. Verify `CELERY_BROKER_URL` matches Redis URL exactly
3. Check Redis service is running in Railway

### Issue: "Connection refused" to Redis

**Cause**: Redis URL incorrect or Redis service not linked

**Solutions**:
1. Verify Redis service is deployed and running
2. Check Redis URL uses Railway's internal DNS: `redis.railway.internal`
3. Ensure both web and Redis are in same Railway project

### Issue: Worker crashes with memory errors

**Cause**: Railway's free tier has memory limits

**Solutions**:
1. Reduce `--concurrency=2` to `--concurrency=1` in `start.sh`
2. Reduce batch size in `process_transactions.py` (currently 5000)
3. Upgrade to Railway Pro for more memory

## Monitoring

### View Celery Tasks (Optional)

Install Flower for task monitoring:

```bash
# Add to a third Railway service or run locally
celery -A celery_app.celery flower --port=5555
```

## Performance Tips

1. **Adjust concurrency** based on Railway plan:
   - Free tier: `--concurrency=1`
   - Hobby: `--concurrency=2`
   - Pro: `--concurrency=4`

2. **Monitor memory usage** in Railway dashboard

3. **Set task timeouts** (already configured in `celery.py`):
   - Hard limit: 1 hour
   - Soft limit: 55 minutes

4. **Use Redis connection pooling** (already configured)

## Next Steps

1. Test the upload endpoint with a sample CSV
2. Monitor the `/celery-health` endpoint
3. Check Railway logs for any errors
4. Consider splitting into two services for production scalability
