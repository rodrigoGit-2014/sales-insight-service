-- Materialized Views for Sales Analytics Performance Optimization
-- These views pre-aggregate data to speed up analytical queries

-- Drop existing materialized views (if any)
DROP MATERIALIZED VIEW IF EXISTS mv_daily_sales CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_monthly_trend CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_department_analytics CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_section_analytics CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_product_analytics CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_customer_top CASCADE;

-- 1. Daily Sales Summary
-- Aggregates sales data by date for fast date-range queries
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT
    company_id,
    fecha,
    SUM(precio_total) AS total_sales,
    COUNT(DISTINCT id_pedido) AS order_count,
    COUNT(DISTINCT id_cliente) AS client_count,
    COUNT(*) AS total_rows,
    AVG(precio_total) AS avg_order_value
FROM tickets
GROUP BY company_id, fecha
ORDER BY fecha;

-- Index for date-based filtering
CREATE INDEX idx_mv_daily_sales_fecha ON mv_daily_sales(fecha);
CREATE INDEX idx_mv_daily_sales_company ON mv_daily_sales(company_id);

-- 2. Monthly Sales Trend
-- Aggregates sales by year and month for trend analysis
CREATE MATERIALIZED VIEW mv_monthly_trend AS
SELECT
    company_id,
    EXTRACT(YEAR FROM fecha)::INTEGER AS year,
    EXTRACT(MONTH FROM fecha)::INTEGER AS month,
    SUM(precio_total) AS total_sales,
    COUNT(DISTINCT id_pedido) AS order_count,
    COUNT(DISTINCT id_cliente) AS client_count,
    AVG(precio_total) AS avg_order_value
FROM tickets
GROUP BY company_id, year, month
ORDER BY year, month;

-- Index for year/month filtering
CREATE INDEX idx_mv_monthly_trend_year_month ON mv_monthly_trend(year, month);
CREATE INDEX idx_mv_monthly_trend_company ON mv_monthly_trend(company_id);

-- 3. Department Analytics
-- Pre-aggregated sales data by department and date
CREATE MATERIALIZED VIEW mv_department_analytics AS
SELECT
    company_id,
    fecha,
    id_departamento,
    SUM(precio_total) AS total_sales,
    COUNT(DISTINCT id_pedido) AS order_count,
    COUNT(DISTINCT id_cliente) AS client_count,
    SUM(cantidad) AS total_quantity
FROM tickets
GROUP BY company_id, fecha, id_departamento
ORDER BY fecha, id_departamento;

-- Indexes for filtering
CREATE INDEX idx_mv_department_analytics_fecha ON mv_department_analytics(fecha);
CREATE INDEX idx_mv_department_analytics_dept ON mv_department_analytics(id_departamento);
CREATE INDEX idx_mv_department_analytics_company ON mv_department_analytics(company_id);

-- 4. Section Analytics
-- Pre-aggregated sales data by section and date
CREATE MATERIALIZED VIEW mv_section_analytics AS
SELECT
    company_id,
    fecha,
    id_departamento,
    id_seccion,
    SUM(precio_total) AS total_sales,
    COUNT(DISTINCT id_pedido) AS order_count,
    COUNT(DISTINCT id_cliente) AS client_count,
    SUM(cantidad) AS total_quantity
FROM tickets
GROUP BY company_id, fecha, id_departamento, id_seccion
ORDER BY fecha, id_departamento, id_seccion;

-- Indexes for filtering
CREATE INDEX idx_mv_section_analytics_fecha ON mv_section_analytics(fecha);
CREATE INDEX idx_mv_section_analytics_section ON mv_section_analytics(id_seccion);
CREATE INDEX idx_mv_section_analytics_dept ON mv_section_analytics(id_departamento);
CREATE INDEX idx_mv_section_analytics_company ON mv_section_analytics(company_id);

-- 5. Product Analytics
-- Pre-aggregated product performance data
CREATE MATERIALIZED VIEW mv_product_analytics AS
SELECT
    company_id,
    fecha,
    id_producto,
    nombre_producto,
    SUM(cantidad) AS total_quantity,
    SUM(precio_total) AS total_revenue,
    COUNT(DISTINCT id_pedido) AS order_count,
    AVG(precio_unitario) AS avg_unit_price,
    MAX(precio_unitario) AS max_unit_price,
    MIN(precio_unitario) AS min_unit_price
FROM tickets
GROUP BY company_id, fecha, id_producto, nombre_producto
ORDER BY fecha, id_producto;

-- Indexes for filtering
CREATE INDEX idx_mv_product_analytics_fecha ON mv_product_analytics(fecha);
CREATE INDEX idx_mv_product_analytics_product ON mv_product_analytics(id_producto);
CREATE INDEX idx_mv_product_analytics_company ON mv_product_analytics(company_id);

-- 6. Top Customers
-- Pre-aggregated customer spending data
CREATE MATERIALIZED VIEW mv_customer_top AS
SELECT
    company_id,
    fecha,
    id_cliente,
    SUM(precio_total) AS total_spent,
    COUNT(DISTINCT id_pedido) AS order_count,
    SUM(cantidad) AS total_items_purchased,
    AVG(precio_total) AS avg_order_value
FROM tickets
GROUP BY company_id, fecha, id_cliente
ORDER BY fecha, id_cliente;

-- Indexes for filtering
CREATE INDEX idx_mv_customer_top_fecha ON mv_customer_top(fecha);
CREATE INDEX idx_mv_customer_top_cliente ON mv_customer_top(id_cliente);
CREATE INDEX idx_mv_customer_top_spent ON mv_customer_top(total_spent DESC);
CREATE INDEX idx_mv_customer_top_company ON mv_customer_top(company_id);

-- Create function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_trend;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_department_analytics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_section_analytics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_product_analytics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_top;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions to the application user
GRANT SELECT ON mv_daily_sales TO PUBLIC;
GRANT SELECT ON mv_monthly_trend TO PUBLIC;
GRANT SELECT ON mv_department_analytics TO PUBLIC;
GRANT SELECT ON mv_section_analytics TO PUBLIC;
GRANT SELECT ON mv_product_analytics TO PUBLIC;
GRANT SELECT ON mv_customer_top TO PUBLIC;

-- Grant execute permission on refresh function
GRANT EXECUTE ON FUNCTION refresh_all_materialized_views() TO PUBLIC;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Materialized views created successfully!';
END $$;
