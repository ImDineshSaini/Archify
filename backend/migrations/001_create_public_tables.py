"""
Initial migration: Create public schema tables

# MIGRATION_SCOPE: public
# MIGRATION_VERSION: 001_create_public_tables
# MIGRATION_DESCRIPTION: Create tenants table in public schema
"""

UPGRADE_SQL = """
-- Tenants table (public schema only)
CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    schema_name VARCHAR(100) UNIQUE NOT NULL,
    admin_email VARCHAR(255) NOT NULL,
    admin_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_trial BOOLEAN DEFAULT TRUE,
    trial_ends_at TIMESTAMP,
    settings TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_tenants_slug ON tenants(slug);
CREATE INDEX IF NOT EXISTS idx_tenants_schema ON tenants(schema_name);
"""

DOWNGRADE_SQL = """
DROP TABLE IF EXISTS tenants CASCADE;
"""


def upgrade():
    """Apply migration"""
    return UPGRADE_SQL


def downgrade():
    """Revert migration"""
    return DOWNGRADE_SQL
