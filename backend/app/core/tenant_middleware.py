from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.core.tenant_db import current_tenant_schema, SessionLocal
from app.core.config import settings
from sqlalchemy import text


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to identify tenant from request and set schema context

    Tenant identification methods:
    1. Subdomain: tenant1.archify.com
    2. Header: X-Tenant-Slug
    3. Query param: ?tenant=tenant1
    """

    async def dispatch(self, request: Request, call_next):
        # Skip tenant identification for public endpoints
        public_paths = [
            '/docs', '/redoc', '/openapi.json',
            '/api/auth/register', '/api/auth/login',
            '/api/tenants/create', '/health', '/'
        ]

        if any(request.url.path.startswith(path) for path in public_paths):
            # Use public schema for these endpoints
            current_tenant_schema.set('public')
            response = await call_next(request)
            return response

        # Identify tenant
        tenant_slug = self._identify_tenant(request)

        if not tenant_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant identification required. Use subdomain, X-Tenant-Slug header, or ?tenant= parameter"
            )

        # Get tenant from database
        db = SessionLocal()
        try:
            db.execute(text('SET search_path TO public'))
            tenant = db.query(Tenant).filter(
                Tenant.slug == tenant_slug,
                Tenant.is_active == True
            ).first()

            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tenant '{tenant_slug}' not found or inactive"
                )

            # Set tenant schema in context
            current_tenant_schema.set(tenant.schema_name)

            # Add tenant info to request state
            request.state.tenant = tenant

        finally:
            db.close()

        response = await call_next(request)
        return response

    def _identify_tenant(self, request: Request) -> Optional[str]:
        """Identify tenant from request using multiple methods"""

        # Method 1: Check subdomain
        host = request.headers.get('host', '')
        if '.' in host and not host.startswith('localhost'):
            subdomain = host.split('.')[0]
            if subdomain and subdomain not in ['www', 'api']:
                return subdomain

        # Method 2: Check X-Tenant-Slug header
        tenant_slug = request.headers.get('X-Tenant-Slug')
        if tenant_slug:
            return tenant_slug

        # Method 3: Check query parameter
        tenant_slug = request.query_params.get('tenant')
        if tenant_slug:
            return tenant_slug

        return None


def get_current_tenant(request: Request) -> Tenant:
    """Dependency to get current tenant from request"""
    if not hasattr(request.state, 'tenant'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tenant context available"
        )
    return request.state.tenant
