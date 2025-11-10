"""
Initial migration: Create tenant schema tables

# MIGRATION_SCOPE: tenant
# MIGRATION_VERSION: 002_create_tenant_tables
# MIGRATION_DESCRIPTION: Create users, repositories, analyses, settings tables in tenant schemas
"""

UPGRADE_SQL = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    source VARCHAR(50) NOT NULL,
    description TEXT,
    language VARCHAR(100),
    stars INTEGER DEFAULT 0,
    forks INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analyses table
CREATE TABLE IF NOT EXISTS analyses (
    id SERIAL PRIMARY KEY,
    repository_id INTEGER NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    maintainability_score FLOAT,
    reliability_score FLOAT,
    scalability_score FLOAT,
    security_score FLOAT,
    overall_score FLOAT,
    code_metrics JSONB,
    architecture_patterns JSONB,
    dependencies JSONB,
    issues JSONB,
    suggestions TEXT,
    detailed_report JSONB,
    analysis_duration FLOAT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- System settings table
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_repositories_user ON repositories(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_repository ON analyses(repository_id);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
CREATE INDEX IF NOT EXISTS idx_settings_key ON system_settings(key);
"""

DOWNGRADE_SQL = """
DROP TABLE IF EXISTS analyses CASCADE;
DROP TABLE IF EXISTS repositories CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS system_settings CASCADE;
"""


def upgrade():
    """Apply migration"""
    return UPGRADE_SQL


def downgrade():
    """Revert migration"""
    return DOWNGRADE_SQL
