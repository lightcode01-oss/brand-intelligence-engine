-- Nomen Relational Database Base Schema Initialization
-- Note: Alembic migrations will manage live modifications.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Health verification check table
CREATE TABLE IF NOT EXISTS system_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO system_checks (status) VALUES ('initialized');
