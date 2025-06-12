-- Create database if it doesn't exist
SELECT 'CREATE DATABASE agri_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'agri_db')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE agri_db TO postgres;

-- Create extensions (if needed)
\c agri_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; 