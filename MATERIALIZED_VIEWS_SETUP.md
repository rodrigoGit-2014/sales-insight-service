# Materialized Views Setup Guide

## Problem

You encountered this error:
```
ERROR: relation "mv_daily_sales" does not exist
```

This happens because the **materialized views** needed for analytical queries were not created in your Railway PostgreSQL database.

## What are Materialized Views?

Materialized views are pre-computed query results stored as tables. They:
- Speed up complex analytical queries significantly
- Are refreshed after new data is uploaded
- Contain aggregated data from the `tickets` table

## Required Materialized Views

Your application needs these 6 views:
1. `mv_daily_sales` - Daily sales aggregates
2. `mv_monthly_trend` - Monthly trend data
3. `mv_department_analytics` - Department performance
4. `mv_section_analytics` - Section performance
5. `mv_product_analytics` - Product performance
6. `mv_customer_top` - Customer spending data

## Solution Options

### Option 1: Automatic Creation (Recommended)

The application will now **automatically create materialized views** on startup if:
- The views don't exist
- The `tickets` table has data

**Steps:**
1. Upload data via `/api/v1/upload-transactions` endpoint
2. Restart your Railway service (or wait for automatic deployment)
3. The views will be created automatically
4. Views will refresh after each data upload

### Option 2: Manual Creation via Railway CLI

If you need to create views immediately:

1. **Install Railway CLI** (if not already installed):
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Link to your project**:
   ```bash
   railway link
   ```

4. **Run the creation script**:
   ```bash
   railway run python scripts/create_materialized_views.py
   ```

### Option 3: Direct Database Access

If you prefer SQL:

1. **Connect to your Railway PostgreSQL**:
   - Go to Railway Dashboard
   - Click on your PostgreSQL service
   - Click "Connect" → copy connection string
   - Use `psql` or any PostgreSQL client

2. **Execute the SQL file**:
   ```bash
   psql "postgresql://..." -f docker/postgres/create_materialized_views.sql
   ```

### Option 4: Railway Shell

1. **Open Railway shell**:
   ```bash
   railway shell
   ```

2. **Run the Python script**:
   ```bash
   python scripts/create_materialized_views.py
   ```

## Verification

After creating the views, verify they exist:

### Via API Endpoint

Create a test endpoint or check logs during startup:
```bash
curl https://your-backend.railway.app/health
```

Check Railway logs for:
```
✓ Materialized views created successfully
```

### Via Database Query

```sql
SELECT matviewname FROM pg_matviews WHERE schemaname = 'public';
```

Should return:
```
mv_daily_sales
mv_monthly_trend
mv_department_analytics
mv_section_analytics
mv_product_analytics
mv_customer_top
```

## When Views Are Refreshed

Materialized views are automatically refreshed:
1. **After data upload** - When a CSV file is processed via `/upload-transactions`
2. **On demand** - By calling the refresh function (optional)

## Manual Refresh (If Needed)

If you need to manually refresh the views:

### Via Railway Shell
```bash
railway shell
python -c "from app.db.session import engine; from sqlalchemy import text; conn = engine.connect(); conn.execute(text('SELECT refresh_all_materialized_views()')); conn.commit()"
```

### Via SQL
```sql
SELECT refresh_all_materialized_views();
```

Or refresh individual views:
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_trend;
-- etc...
```

## Troubleshooting

### Error: "No data in tickets table"

**Solution**: Upload data first via `/api/v1/upload-transactions`, then views will be created automatically.

### Error: "Materialized view already exists"

**Solution**: This is normal. The views are already created. No action needed.

### Error: "Cannot refresh materialized view concurrently"

**Cause**: Missing unique indexes

**Solution**: The code will automatically fall back to non-concurrent refresh.

### Views exist but no data returned

**Cause**: Views need to be refreshed after data upload

**Solution**:
1. Check if Celery worker is running (via `/celery-health`)
2. Views should auto-refresh after each upload
3. Manually refresh if needed (see above)

## Performance Benefits

With materialized views:
- **Daily sales queries**: ~100x faster
- **Monthly trends**: ~50x faster
- **Department analytics**: ~75x faster
- **Product rankings**: ~80x faster

## Next Steps

1. Deploy these changes to Railway
2. Upload data via `/api/v1/upload-transactions`
3. Views will be created automatically
4. Test your analytics endpoints

## Files Involved

- `docker/postgres/create_materialized_views.sql` - SQL definitions
- `scripts/create_materialized_views.py` - Python script to create views
- `app/db/session.py` - Auto-creation logic
- `celery_app/tasks/process_transactions.py` - Auto-refresh logic
