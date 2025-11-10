# Multi-Tenancy Architecture Guide

## Overview

Archify supports **schema-based multi-tenancy** using PostgreSQL schemas. Each tenant (organization) gets:
- ✅ Isolated PostgreSQL schema
- ✅ Separate database tables
- ✅ Independent data storage
- ✅ Complete data isolation
- ✅ Automatic setup and migration
- ✅ Dedicated admin user

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              PostgreSQL Database                      │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────┐     ┌──────────────┐              │
│  │   public    │     │ tenant_acme  │              │
│  │   schema    │     │   schema     │              │
│  ├─────────────┤     ├──────────────┤              │
│  │ - tenants   │     │ - users      │              │
│  │             │     │ - repos      │              │
│  └─────────────┘     │ - analyses   │              │
│                      │ - settings   │              │
│  ┌──────────────┐    └──────────────┘              │
│  │tenant_corp   │                                   │
│  │  schema      │    ┌──────────────┐              │
│  ├──────────────┤    │tenant_startup│              │
│  │ - users      │    │   schema     │              │
│  │ - repos      │    ├──────────────┤              │
│  │ - analyses   │    │ - users      │              │
│  │ - settings   │    │ - repos      │              │
│  └──────────────┘    │ - analyses   │              │
│                      │ - settings   │              │
│                      └──────────────┘              │
└─────────────────────────────────────────────────────┘
```

## Enabling Multi-Tenancy

### 1. Update Environment Configuration

Edit `.env` file:

```bash
# Enable multi-tenancy mode
ENABLE_MULTI_TENANCY=true
```

### 2. Restart the Application

```bash
# With Docker
docker compose restart backend

# Local development
# Restart your backend server
```

## Tenant Identification

The system identifies tenants using three methods (in order of priority):

### Method 1: Subdomain (Recommended for Production)
```
https://acme.archify.com/
https://corp.archify.com/
```

### Method 2: HTTP Header
```bash
curl -H "X-Tenant-Slug: acme" https://api.archify.com/api/repositories
```

### Method 3: Query Parameter (Development)
```
https://api.archify.com/api/repositories?tenant=acme
```

## Creating a Tenant

### Via API

```bash
curl -X POST http://localhost:8000/api/tenants/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "slug": "acme",
    "admin_email": "admin@acme.com",
    "admin_name": "John Doe",
    "admin_password": "securepassword123"
  }'
```

### Via UI

1. Navigate to **Tenants** in the sidebar
2. Click **Create Tenant**
3. Fill in the form:
   - **Organization Name**: Human-readable name
   - **Slug**: URL-safe identifier (auto-generated)
   - **Admin Email**: Email for tenant admin
   - **Admin Name**: Full name of admin
   - **Admin Password**: Password for tenant's admin user
4. Click **Create Tenant**

### What Happens During Tenant Creation?

1. ✅ Validates tenant slug format
2. ✅ Creates tenant record in `public.tenants` table
3. ✅ Creates new PostgreSQL schema: `tenant_{slug}`
4. ✅ Creates all tables in tenant schema:
   - users
   - repositories
   - analyses
   - system_settings
5. ✅ Seeds admin user in tenant schema
6. ✅ Returns tenant information

## Using a Tenant

### Frontend Configuration

Add tenant slug to API calls:

```javascript
// Set tenant header
axios.defaults.headers.common['X-Tenant-Slug'] = 'acme';

// OR use query parameter
const response = await axios.get('/api/repositories?tenant=acme');
```

### Login as Tenant User

```bash
# Login with tenant's admin user
curl -X POST http://localhost:8000/api/auth/login?tenant=acme \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_acme",
    "password": "securepassword123"
  }'
```

### Frontend Access

```
http://localhost:3000/?tenant=acme
```

Or configure subdomain routing:
```
http://acme.localhost:3000/
```

## Data Isolation

### How Data is Isolated

1. **Schema-level isolation**: Each tenant has a dedicated PostgreSQL schema
2. **Connection-level isolation**: Database connections set `search_path` to tenant schema
3. **Middleware enforcement**: Tenant middleware validates and routes all requests
4. **No cross-tenant queries**: Impossible to query another tenant's data

### Shared Data (Public Schema)

Only the following is stored in `public` schema:
- Tenant registry (tenant metadata)
- No user data
- No repository data
- No analysis data

### Example Schema Structure

```sql
-- Public schema (shared)
public.tenants
  - id, name, slug, schema_name, admin_email, is_active

-- Tenant schema (isolated)
tenant_acme.users
  - id, email, username, hashed_password

tenant_acme.repositories
  - id, user_id, name, url, source

tenant_acme.analyses
  - id, repository_id, status, scores
```

## Managing Tenants

### List All Tenants

```bash
curl http://localhost:8000/api/tenants
```

### Get Tenant Details

```bash
curl http://localhost:8000/api/tenants/1
```

### Update Tenant

```bash
curl -X PUT http://localhost:8000/api/tenants/1 \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

### Delete Tenant (⚠️ Destructive)

```bash
curl -X DELETE http://localhost:8000/api/tenants/1
```

**Warning**: This permanently deletes:
- The tenant's schema
- All tables in the schema
- All user data
- All repository data
- All analysis data

## Security Considerations

### 1. Tenant Validation

The middleware ensures:
- Tenant exists in database
- Tenant is active
- Valid tenant identification
- Proper schema routing

### 2. Data Access Control

- Users can only access their tenant's data
- No cross-tenant API calls possible
- Schema-level isolation enforced at database level
- Middleware validates tenant context on every request

### 3. Admin Access

- Tenant management endpoints are public (need auth in production)
- Consider adding super-admin role for tenant management
- Implement tenant-level admin permissions

### 4. Production Security Checklist

- [ ] Add authentication to tenant management endpoints
- [ ] Implement super-admin role
- [ ] Add rate limiting per tenant
- [ ] Enable SSL/TLS for all connections
- [ ] Use subdomain routing instead of query parameters
- [ ] Implement tenant activity logging
- [ ] Add tenant usage quotas
- [ ] Enable backup per tenant schema

## Migration Guide

### Migrating Existing Single-Tenant Installation

If you have existing data:

1. **Backup your database**
   ```bash
   pg_dump archify > backup.sql
   ```

2. **Create a tenant for existing data**
   ```bash
   curl -X POST http://localhost:8000/api/tenants/create \
     -d '{"name": "Default", "slug": "default", ...}'
   ```

3. **Migrate existing data to tenant schema**
   ```sql
   -- Move data from public to tenant schema
   INSERT INTO tenant_default.users
   SELECT * FROM public.users;

   INSERT INTO tenant_default.repositories
   SELECT * FROM public.repositories;

   -- etc.
   ```

4. **Enable multi-tenancy**
   ```bash
   ENABLE_MULTI_TENANCY=true
   ```

5. **Update frontend to use tenant slug**
   ```javascript
   axios.defaults.headers.common['X-Tenant-Slug'] = 'default';
   ```

### Adding New Tenants to Existing Multi-Tenant Setup

Simply use the tenant creation API or UI - no migration needed!

## Database Maintenance

### Backup Individual Tenant

```bash
pg_dump -n tenant_acme archify > tenant_acme_backup.sql
```

### Restore Tenant

```bash
psql archify < tenant_acme_backup.sql
```

### Monitor Tenant Schema Sizes

```sql
SELECT
    nspname AS schema_name,
    pg_size_pretty(sum(pg_relation_size(C.oid))) AS size
FROM pg_class C
LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
WHERE nspname LIKE 'tenant_%'
GROUP BY nspname
ORDER BY sum(pg_relation_size(C.oid)) DESC;
```

## Performance Optimization

### Connection Pooling

Each tenant connection sets the schema:
```sql
SET search_path TO "tenant_acme", public;
```

### Indexes

Indexes are created per schema, ensuring optimal performance per tenant.

### Schema Limits

PostgreSQL can handle thousands of schemas. Recommended limits:
- **Small tenants (<100 users)**: 10,000+ schemas
- **Medium tenants (100-1000 users)**: 1,000+ schemas
- **Large tenants (1000+ users)**: Consider sharding

## Troubleshooting

### Tenant Not Found Error

```
HTTP 404: Tenant 'acme' not found or inactive
```

**Solutions:**
1. Check tenant exists: `SELECT * FROM public.tenants WHERE slug='acme'`
2. Verify tenant is active: `is_active = true`
3. Check tenant slug spelling

### Schema Creation Failed

```
Failed to create tenant schema
```

**Solutions:**
1. Check PostgreSQL user permissions
2. Ensure database has space
3. Check logs: `docker compose logs backend`

### Cross-Tenant Data Leakage

**Prevention:**
- Middleware enforces tenant context
- Schema isolation at database level
- No way to query across schemas without explicit permissions

**Verification:**
```sql
-- This should return only one schema
SHOW search_path;
```

## Best Practices

### 1. Naming Conventions

- **Tenant slugs**: lowercase, alphanumeric, hyphens only
- **Schema names**: `tenant_{slug}` (auto-generated)
- **Admin usernames**: `admin_{slug}` (auto-generated)

### 2. Production Deployment

- Use subdomain routing
- Implement tenant-based rate limiting
- Add tenant usage analytics
- Enable per-tenant backups
- Monitor schema sizes

### 3. Development

- Use query parameter for tenant identification
- Test with multiple tenants
- Verify data isolation
- Test tenant creation/deletion

### 4. Monitoring

- Track tenant creation
- Monitor schema sizes
- Alert on inactive tenants
- Log tenant-specific errors

## API Reference

### Create Tenant

```
POST /api/tenants/create
```

**Request:**
```json
{
  "name": "Acme Corporation",
  "slug": "acme",
  "admin_email": "admin@acme.com",
  "admin_name": "John Doe",
  "admin_password": "securepass"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "slug": "acme",
  "schema_name": "tenant_acme",
  "admin_email": "admin@acme.com",
  "is_active": true,
  "is_trial": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### List Tenants

```
GET /api/tenants
```

### Get Tenant

```
GET /api/tenants/{id}
```

### Update Tenant

```
PUT /api/tenants/{id}
```

**Request:**
```json
{
  "is_active": false,
  "is_trial": false
}
```

### Delete Tenant

```
DELETE /api/tenants/{id}
```

## FAQ

**Q: Can I disable multi-tenancy after enabling it?**
A: Yes, set `ENABLE_MULTI_TENANCY=false` and restart.

**Q: What happens to existing tenants if I disable multi-tenancy?**
A: Tenant schemas remain but won't be used. You'll need to manually migrate data.

**Q: How many tenants can I have?**
A: PostgreSQL can handle 10,000+ schemas easily. Practical limit depends on your database size.

**Q: Can tenants have custom domains?**
A: Yes! Configure DNS and subdomain routing in your reverse proxy (Nginx/Traefik).

**Q: Is there a performance impact?**
A: Minimal. Each request sets the schema, which is very fast. Indexes are per-schema for optimal performance.

**Q: Can I move a tenant to a different database?**
A: Yes, export the schema and import to another database:
```bash
pg_dump -n tenant_acme src_db | psql dest_db
```

**Q: How do I implement tenant-specific billing?**
A: Track usage in tenant record, add billing fields to `Tenant` model.

---

For more information, see:
- [README.md](README.md) - General setup
- [LOCAL_SETUP.md](LOCAL_SETUP.md) - Local development
- [Backend API Docs](http://localhost:8000/docs) - API documentation
