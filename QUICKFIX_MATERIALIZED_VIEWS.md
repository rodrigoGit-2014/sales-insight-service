# Quick Fix: Materialized Views Missing

## The Issue
```
ERROR: relation "mv_daily_sales" does not exist
```

## The Solution (Automatic)

The code has been updated to **automatically create materialized views** when:
1. The application starts
2. Data exists in the tickets table
3. Views don't already exist

## What You Need to Do

### Option 1: Let It Auto-Fix (Easiest)

1. **Deploy these changes** (commit and push)
2. **Upload data** via `/api/v1/upload-transactions` if you haven't already
3. **Restart the Railway service** (or it will restart automatically on deploy)
4. Views will be created automatically ✅

### Option 2: Create Views Manually (Railway CLI)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run the script
railway run python scripts/create_materialized_views.py
```

## Verify It Worked

Check this endpoint after deployment:
```bash
curl https://your-backend.railway.app/db-health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "ticket_count": 1234,
  "materialized_views": {
    "total": 6,
    "required": 6,
    "missing": [],
    "views": [...]
  },
  "message": "All systems operational"
}
```

## What Was Changed

1. ✅ Created SQL file with materialized view definitions
2. ✅ Added auto-creation logic on app startup
3. ✅ Added auto-refresh after data upload
4. ✅ Added manual creation script
5. ✅ Added `/db-health` endpoint for monitoring
6. ✅ Updated Dockerfile to include necessary files

## Next Steps

1. Commit and push changes
2. Wait for Railway deployment
3. Check `/db-health` endpoint
4. Test your analytics endpoints

That's it! The error should be fixed automatically.
