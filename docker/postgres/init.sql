-- Initialization script for Sales Analytics Database

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create job_status enum type
CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed');

-- Create tickets table
CREATE TABLE IF NOT EXISTS tickets (
    id BIGSERIAL PRIMARY KEY,
    id_pedido VARCHAR(100) NOT NULL,
    id_cliente VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    id_departamento VARCHAR(50) NOT NULL,
    id_seccion VARCHAR(50) NOT NULL,
    id_producto VARCHAR(100) NOT NULL,
    nombre_producto VARCHAR(500) NOT NULL,
    precio_unitario NUMERIC(12, 2) NOT NULL CHECK (precio_unitario >= 0),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_total NUMERIC(12, 2) NOT NULL CHECK (precio_total >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for tickets table
CREATE INDEX IF NOT EXISTS idx_tickets_fecha ON tickets(fecha);
CREATE INDEX IF NOT EXISTS idx_tickets_id_cliente ON tickets(id_cliente);
CREATE INDEX IF NOT EXISTS idx_tickets_id_producto ON tickets(id_producto);
CREATE INDEX IF NOT EXISTS idx_tickets_id_departamento ON tickets(id_departamento);
CREATE INDEX IF NOT EXISTS idx_tickets_id_seccion ON tickets(id_seccion);
CREATE INDEX IF NOT EXISTS idx_tickets_fecha_cliente ON tickets(fecha, id_cliente);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_fecha_producto ON tickets(fecha, id_producto);

-- Create jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status job_status NOT NULL DEFAULT 'pending',
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    total_rows INTEGER,
    processed_rows INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for jobs table
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for tickets table
CREATE TRIGGER update_tickets_updated_at
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sales_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sales_user;
