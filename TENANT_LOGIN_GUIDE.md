# Tenant Login Guide

## 🏢 Multi-Tenant Login Feature

The application now supports **tenant-aware login** for multi-tenant deployments!

---

## 📍 Login URLs

### Option 1: Standard Login (with tenant field)
```
http://localhost:3000/login
```
- Shows a tenant field (optional)
- Can toggle between tenant/non-tenant login
- Best for: Development and testing

### Option 2: Tenant-Specific URL
```
http://localhost:3000/tenant/acme/login
```
- Pre-fills the tenant slug from URL
- Cleaner UX for users
- Best for: Production deployments

### Option 3: Query Parameter
```
http://localhost:3000/login?tenant=acme
```
- Passes tenant via query string
- Alternative URL format

---

## 🎯 How It Works

### For Users:
1. **Go to login page**
2. **Enter tenant slug** (if enabled):
   - Example: `acme` for Acme Corp
   - Leave empty for single-tenant mode
3. **Enter username and password**
4. **Sign in**

### Behind the Scenes:
- Uses `/api/v2/auth/login` endpoint (supports tenants)
- Sends tenant slug in `X-Tenant-Slug` header
- JWT token includes tenant context
- User is isolated to their tenant's data

---

## 🔧 Setup Instructions

### 1. Enable Multi-Tenancy (Backend)

In `.env`:
```bash
ENABLE_MULTI_TENANCY=true
```

### 2. Create Tenants

**Via Web UI:**
1. Login as admin
2. Go to `/tenants` page
3. Click "Create Tenant"
4. Fill in details:
   - Organization Name: `Acme Corp`
   - Slug: `acme`
   - Admin Email: `admin@acme.com`
   - Admin Password: `secure123`

**Via API:**
```bash
curl -X POST http://localhost:8000/api/tenants \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Acme Corp",
    "slug": "acme",
    "admin_email": "admin@acme.com",
    "admin_name": "Acme Admin",
    "admin_password": "secure123"
  }'
```

### 3. Login to Tenant

**Option A - Via Tenant URL:**
```
http://localhost:3000/tenant/acme/login
Username: admin@acme.com
Password: secure123
```

**Option B - Via Standard Login:**
```
http://localhost:3000/login
Tenant: acme
Username: admin@acme.com
Password: secure123
```

---

## 🎨 UI Features

### Tenant Selection
- **Optional field** in standard login
- **Toggle button** to switch between tenant/non-tenant mode
- **Auto-generated slug** from organization name in tenant creation

### Visual Indicators
- Tenant name shown as **chip badge**
- Organization icon for tenant login
- Info messages about multi-tenancy

### User Experience
- Smooth tenant switching
- Clear error messages
- Remembers tenant in localStorage

---

## 🏗️ Architecture

### Frontend Components

**TenantLogin.jsx** (NEW):
- Supports all 3 login URL formats
- Shows/hides tenant field dynamically
- Uses v2 auth API with tenant support

**Routes:**
```jsx
/login                    → TenantLogin (with optional tenant field)
/tenant-login            → TenantLogin (explicit tenant login)
/tenant/:slug/login      → TenantLogin (pre-filled tenant)
```

### Backend Support

**Auth V2 API:**
```python
POST /api/v2/auth/login
Header: X-Tenant-Slug: acme
Body: {
  "username": "user@example.com",
  "password": "password123"
}
```

**Token Contents:**
```json
{
  "sub": "username",
  "user_id": 1,
  "is_admin": false,
  "tenant_slug": "acme",
  "tenant_schema": "tenant_acme"
}
```

---

## 🔐 Security

### Tenant Isolation
- Each tenant has isolated PostgreSQL schema
- Data is completely separated
- No cross-tenant data access

### Authentication
- JWT tokens include tenant context
- Tokens are tenant-specific
- Rate limiting per IP (5 attempts/min)

### Authorization
- Users can only access their tenant's data
- Tenant middleware enforces isolation
- Admin users can manage their tenant

---

## 📊 Testing

### Test Scenarios

**1. Single-Tenant Login:**
```
URL: /login
Tenant: [empty]
Username: testuser
Password: password123
✓ Should login without tenant context
```

**2. Multi-Tenant Login:**
```
URL: /login
Tenant: acme
Username: admin@acme.com
Password: secure123
✓ Should login to Acme tenant
```

**3. URL-based Tenant:**
```
URL: /tenant/acme/login
Username: admin@acme.com
Password: secure123
✓ Should pre-fill tenant from URL
```

**4. Wrong Tenant:**
```
Tenant: acme
Username: bob@contoso.com (different tenant)
✗ Should fail - user not in this tenant
```

---

## 🚀 Production Deployment

### Subdomain Setup (Recommended)

**Setup DNS:**
```
acme.archify.com    → Your app
contoso.archify.com → Your app
```

**Configure Frontend:**
```javascript
// Extract tenant from subdomain
const hostname = window.location.hostname;
const tenant = hostname.split('.')[0];

// Auto-login to tenant
if (tenant && tenant !== 'www') {
  navigate(`/tenant/${tenant}/login`);
}
```

**Nginx/Reverse Proxy:**
```nginx
server {
    listen 80;
    server_name *.archify.com;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header X-Tenant-Slug $host;
    }
}
```

### Environment Variables

**Production `.env`:**
```bash
# Enable multi-tenancy
ENABLE_MULTI_TENANCY=true

# Update CORS for tenant subdomains
CORS_ORIGINS=https://*.archify.com

# Secure secrets
SECRET_KEY=your-production-secret
JWT_SECRET_KEY=your-production-jwt-secret
```

---

## 🎯 Usage Examples

### Example 1: SaaS Platform
```
Company A → https://companya.archify.com/login
Company B → https://companyb.archify.com/login
Each company sees only their data!
```

### Example 2: Enterprise Deployment
```
Department 1 → https://app.company.com/tenant/dept1/login
Department 2 → https://app.company.com/tenant/dept2/login
Isolated workspaces for each department!
```

### Example 3: Development
```
Single tenant: http://localhost:3000/login
Multi tenant:  http://localhost:3000/login (enter tenant manually)
Direct access: http://localhost:3000/tenant/acme/login
```

---

## 📝 Summary

✅ **Three login URL options** for flexibility
✅ **Tenant isolation** at database level
✅ **Clean UX** with optional tenant field
✅ **Production-ready** with subdomain support
✅ **Backwards compatible** with single-tenant mode

**Now your users can login to their specific tenant/organization!** 🎉
