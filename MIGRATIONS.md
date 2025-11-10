# Database Migration Guide

## Overview

Archify uses a **custom migration system** designed for multi-tenant PostgreSQL schemas. The system automatically handles:

- ✅ **Public schema migrations** (tenant registry, system tables)
- ✅ **Tenant schema migrations** (user data tables)
- ✅ **Automatic migration** for newly created tenants
- ✅ **Migration tracking** per schema
- ✅ **Rollback support**

## Migration Architecture

```
migrations/
├── 001_create_public_tables.py     # SCOPE: public
├── 002_create_tenant_tables.py     # SCOPE: tenant
├── 003_add_user_avatar.py          # SCOPE: tenant
└── 004_add_system_config.py        # SCOPE: both
```

Each migration is tagged with a **scope**:
- `public` - Only applies to public schema
- `tenant` - Applies to all tenant schemas
- `both` - Applies to both public and tenant schemas

## Migration Tracking

Each schema has a `schema_migrations` table:

```sql
CREATE TABLE schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

This tracks which migrations have been applied to each schema.

## Creating Migrations

### Migration Template

```python
"""
Migration description

# MIGRATION_SCOPE: tenant|public|both
# MIGRATION_VERSION: 003_add_user_avatar
# MIGRATION_DESCRIPTION: Add avatar_url column to users table
"""

UPGRADE_SQL = """
ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500);
"""

DOWNGRADE_SQL = """
ALTER TABLE users DROP COLUMN avatar_url;
"""


def upgrade():
    """Apply migration"""
    return UPGRADE_SQL


def downgrade():
    """Revert migration"""
    return DOWNGRADE_SQL
```

### Migration Metadata

**Required comments in migration file:**

```python
# MIGRATION_SCOPE: public|tenant|both
# MIGRATION_VERSION: 003_migration_name
# MIGRATION_DESCRIPTION: What this migration does
```

### Migration Scopes Explained

#### 1. Public Scope
```python
# MIGRATION_SCOPE: public
```

- Applies **only** to `public` schema
- Use for: tenant registry, system-wide tables
- Example: Adding columns to `tenants` table

#### 2. Tenant Scope
```python
# MIGRATION_SCOPE: tenant
```

- Applies to **all tenant schemas** (`tenant_acme`, `tenant_corp`, etc.)
- Does **not** apply to public schema
- Use for: user data tables, repositories, analyses
- Example: Adding `avatar_url` to `users` table

#### 3. Both Scopes
```python
# MIGRATION_SCOPE: both
```

- Applies to **both** public and all tenant schemas
- Use for: features that span both scopes
- Example: Adding audit logging tables

## Running Migrations

### CLI Commands

```bash
# Show migration status
python -m app.cli.migrate status

# Migrate public schema only
python -m app.cli.migrate public

# Migrate all tenant schemas
python -m app.cli.migrate tenants

# Migrate specific tenant
python -m app.cli.migrate tenant acme

# Migrate everything (public + all tenants)
python -m app.cli.migrate all
```

### Docker Commands

```bash
# Show status
docker compose exec backend python -m app.cli.migrate status

# Migrate public
docker compose exec backend python -m app.cli.migrate public

# Migrate all tenants
docker compose exec backend python -m app.cli.migrate tenants

# Migrate specific tenant
docker compose exec backend python -m app.cli.migrate tenant acme

# Migrate everything
docker compose exec backend python -m app.cli.migrate all
```

### Makefile Shortcuts

```bash
# Show migration status
make migrate-status

# Migrate public schema
make migrate-public

# Migrate all tenant schemas
make migrate-tenants

# Migrate specific tenant
make migrate-tenant TENANT=acme

# Migrate everything
make migrate-all
```

## Migration Workflow

### 1. Check Status

```bash
make migrate-status
```

Output:
```
============================================================
MIGRATION STATUS
============================================================

📊 Public Schema:
  Applied: 1
  Pending: 0

  Applied migrations:
    ✓ 001_create_public_tables

🏢 Tenant Schemas: 3

  acme (tenant_acme):
    Applied: 2
    Pending: 1
      ⏳ 003_add_user_avatar

  corp (tenant_corp):
    Applied: 2
    Pending: 1
      ⏳ 003_add_user_avatar

  startup (tenant_startup):
    Applied: 1
    Pending: 2
      ⏳ 002_create_tenant_tables
      ⏳ 003_add_user_avatar
============================================================
```

### 2. Apply Migrations

```bash
# Migrate specific scope
make migrate-tenants

# Or migrate everything
make migrate-all
```

Output:
```
🔄 Migrating all tenant schemas...

  tenant_acme:
    ✓ 003_add_user_avatar

  tenant_corp:
    ✓ 003_add_user_avatar

  tenant_startup:
    ✓ 002_create_tenant_tables
    ✓ 003_add_user_avatar

✅ Tenant migration complete
```

## New Tenant Creation

When a new tenant is created via API:

```bash
POST /api/tenants/create
{
  "name": "New Corp",
  "slug": "newcorp",
  ...
}
```

**Automatic migration process:**

1. ✅ Creates PostgreSQL schema: `tenant_newcorp`
2. ✅ Initializes migration tracking table
3. ✅ Applies **all pending tenant migrations** automatically
4. ✅ Seeds admin user
5. ✅ Returns ready-to-use tenant

**No manual migration needed!**

## Example Migrations

### Example 1: Add Column to Tenant Tables

**File:** `migrations/003_add_user_avatar.py`

```python
"""
Add avatar URL to users

# MIGRATION_SCOPE: tenant
# MIGRATION_VERSION: 003_add_user_avatar
# MIGRATION_DESCRIPTION: Add avatar_url column to users table
"""

UPGRADE_SQL = """
ALTER TABLE users
ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS bio TEXT;

CREATE INDEX IF NOT EXISTS idx_users_avatar ON users(avatar_url);
"""

DOWNGRADE_SQL = """
ALTER TABLE users
DROP COLUMN IF EXISTS avatar_url,
DROP COLUMN IF EXISTS bio;
"""


def upgrade():
    return UPGRADE_SQL


def downgrade():
    return DOWNGRADE_SQL
```

**Apply to all tenants:**
```bash
make migrate-tenants
```

### Example 2: Modify Public Schema

**File:** `migrations/004_add_tenant_billing.py`

```python
"""
Add billing information to tenants

# MIGRATION_SCOPE: public
# MIGRATION_VERSION: 004_add_tenant_billing
# MIGRATION_DESCRIPTION: Add billing fields to tenants table
"""

UPGRADE_SQL = """
ALTER TABLE tenants
ADD COLUMN IF NOT EXISTS billing_email VARCHAR(255),
ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free',
ADD COLUMN IF NOT EXISTS subscription_ends_at TIMESTAMP;
"""

DOWNGRADE_SQL = """
ALTER TABLE tenants
DROP COLUMN IF EXISTS billing_email,
DROP COLUMN IF EXISTS subscription_tier,
DROP COLUMN IF EXISTS subscription_ends_at;
"""


def upgrade():
    return UPGRADE_SQL


def downgrade():
    return DOWNGRADE_SQL
```

**Apply to public schema:**
```bash
make migrate-public
```

### Example 3: Migration for Both Scopes

**File:** `migrations/005_add_audit_logs.py`

```python
"""
Add audit logging tables

# MIGRATION_SCOPE: both
# MIGRATION_VERSION: 005_add_audit_logs
# MIGRATION_DESCRIPTION: Create audit_logs table in all schemas
"""

UPGRADE_SQL = """
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id INTEGER,
    metadata JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);
"""

DOWNGRADE_SQL = """
DROP TABLE IF EXISTS audit_logs;
"""


def upgrade():
    return UPGRADE_SQL


def downgrade():
    return DOWNGRADE_SQL
```

**Apply to all schemas:**
```bash
make migrate-all
```

## Best Practices

### 1. Naming Convention

```
{number}_{descriptive_name}.py

Examples:
001_create_public_tables.py
002_create_tenant_tables.py
003_add_user_avatar.py
004_add_tenant_billing.py
```

Use sequential numbers with leading zeros (001, 002, 003...)

### 2. Always Include Metadata

```python
# MIGRATION_SCOPE: tenant
# MIGRATION_VERSION: 003_add_user_avatar
# MIGRATION_DESCRIPTION: Add avatar_url column to users table
```

### 3. Use IF EXISTS/IF NOT EXISTS

```sql
-- Good
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);

-- Bad
ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500);
```

This makes migrations idempotent and safe to re-run.

### 4. Always Provide Downgrade

```python
DOWNGRADE_SQL = """
ALTER TABLE users DROP COLUMN IF EXISTS avatar_url;
"""
```

### 5. Test Migrations

```bash
# Test on single tenant first
make migrate-tenant TENANT=test

# Check status
make migrate-status

# Then apply to all
make migrate-tenants
```

### 6. Backup Before Major Migrations

```bash
# Backup specific tenant
pg_dump -n tenant_acme archify > backup_tenant_acme.sql

# Backup public schema
pg_dump -n public archify > backup_public.sql

# Backup everything
pg_dump archify > backup_full.sql
```

## Migration Order

Migrations are applied in **filename order**:

```
001_create_public_tables.py     ← First
002_create_tenant_tables.py     ← Second
003_add_user_avatar.py          ← Third
004_add_tenant_billing.py       ← Fourth
```

**Important:** Always use sequential numbering!

## Rollback (Manual)

Currently, rollback must be done manually:

```python
# Get the downgrade SQL from migration file
DOWNGRADE_SQL = """
ALTER TABLE users DROP COLUMN avatar_url;
"""

# Apply manually to schema
psql archify -c "SET search_path TO tenant_acme; ALTER TABLE users DROP COLUMN avatar_url;"

# Remove from migration tracking
psql archify -c "SET search_path TO tenant_acme; DELETE FROM schema_migrations WHERE version = '003_add_user_avatar';"
```

## Troubleshooting

### Migration Failed Midway

```bash
# Check status
make migrate-status

# Verify what was applied
psql archify -c "SET search_path TO tenant_acme; SELECT * FROM schema_migrations;"

# Fix the issue, then retry
make migrate-tenant TENANT=acme
```

### Migration Already Applied

The system tracks applied migrations and skips them automatically.

### Schema Doesn't Exist

```bash
# For tenant schemas, ensure tenant exists
psql archify -c "SELECT * FROM public.tenants WHERE slug = 'acme';"

# Check if schema exists
psql archify -c "\dn tenant_*"
```

### Permission Issues

```sql
-- Grant schema permissions
GRANT ALL ON SCHEMA tenant_acme TO archify;
GRANT ALL ON ALL TABLES IN SCHEMA tenant_acme TO archify;
```

## Advanced Usage

### Check Specific Tenant Status

```python
from app.core.migration_manager import MigrationManager

manager = MigrationManager()

# Get applied migrations
applied = manager.get_applied_migrations("tenant_acme")
print(f"Applied: {applied}")

# Get pending migrations
pending = manager.get_pending_migrations("tenant_acme")
print(f"Pending: {[m['version'] for m in pending]}")
```

### Custom Migration Script

```python
from app.core.migration_manager import MigrationManager
from pathlib import Path

manager = MigrationManager()

# Apply specific migration to specific tenant
migration_file = Path("migrations/003_add_user_avatar.py")
manager.apply_migration_to_schema("tenant_acme", migration_file)
```

## Integration with Alembic (Optional)

If you prefer Alembic for public schema:

1. Keep Alembic for public schema migrations
2. Use this custom system for tenant schema migrations
3. Configure Alembic to only target public schema:

```python
# alembic/env.py
target_metadata = Base.metadata
include_schemas = True
include_symbol = lambda table_name, schema_name: schema_name == "public"
```

## CI/CD Integration

```yaml
# .github/workflows/deploy.yml
- name: Run migrations
  run: |
    docker compose exec -T backend python -m app.cli.migrate status
    docker compose exec -T backend python -m app.cli.migrate all
```

## FAQ

**Q: What happens if a tenant migration fails?**
A: The migration stops for that tenant. Other tenants continue. Fix the issue and re-run.

**Q: Can I apply migrations to just one tenant?**
A: Yes! `make migrate-tenant TENANT=acme`

**Q: Are new tenants automatically migrated?**
A: Yes! All pending tenant migrations are applied during tenant creation.

**Q: How do I add a new table?**
A: Create a new migration file with scope `tenant` or `public` depending on where it belongs.

**Q: Can I rename a table?**
A: Yes, but be careful! Test thoroughly and consider data migration.

**Q: What if I need to migrate data, not just schema?**
A: Add data migration SQL in the same migration file:
```python
UPGRADE_SQL = """
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);
UPDATE users SET full_name = first_name || ' ' || last_name;
ALTER TABLE users DROP COLUMN first_name, DROP COLUMN last_name;
"""
```

**Q: Can I use Python code instead of SQL?**
A: Currently, the system uses SQL migrations. Python migrations would require extending the `MigrationManager`.

---

For more information:
- [MULTI_TENANCY.md](MULTI_TENANCY.md) - Multi-tenancy architecture
- [README.md](README.md) - General setup
