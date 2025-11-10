from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.tenant_db import get_public_db, TenantDatabaseManager
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
import re

router = APIRouter(prefix="/tenants", tags=["Tenants"])


def validate_slug(slug: str) -> bool:
    """Validate tenant slug format"""
    return bool(re.match(r'^[a-z0-9-]+$', slug))


@router.post("/create", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_public_db)
):
    """
    Create a new tenant (organization)
    This creates a new PostgreSQL schema and seeds initial data
    """
    # Validate slug format
    if not validate_slug(tenant_data.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug must contain only lowercase letters, numbers, and hyphens"
        )

    # Check if tenant already exists
    existing = db.query(Tenant).filter(
        (Tenant.slug == tenant_data.slug) | (Tenant.admin_email == tenant_data.admin_email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this slug or admin email already exists"
        )

    # Create schema name from slug
    schema_name = f"tenant_{tenant_data.slug}"

    try:
        # Create tenant record in public schema
        tenant = Tenant(
            name=tenant_data.name,
            slug=tenant_data.slug,
            schema_name=schema_name,
            admin_email=tenant_data.admin_email,
            admin_name=tenant_data.admin_name,
            is_active=True,
            is_trial=True
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        # Create schema for tenant
        TenantDatabaseManager.create_tenant_schema(schema_name)

        # Seed initial data (admin user)
        admin_user_data = {
            'email': tenant_data.admin_email,
            'username': f"admin_{tenant_data.slug}",
            'full_name': tenant_data.admin_name,
            'password': tenant_data.admin_password
        }
        TenantDatabaseManager.seed_tenant_data(schema_name, admin_user_data)

        return tenant

    except Exception as e:
        db.rollback()
        # Cleanup: try to delete schema if tenant creation failed
        try:
            if tenant.id:
                db.delete(tenant)
                db.commit()
            TenantDatabaseManager.delete_tenant_schema(schema_name)
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tenant: {str(e)}"
        )


@router.get("/", response_model=List[TenantResponse])
def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_public_db)
):
    """List all tenants (super admin only)"""
    tenants = db.query(Tenant).offset(skip).limit(limit).all()
    return tenants


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_public_db)
):
    """Get tenant by ID"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: int,
    tenant_update: TenantUpdate,
    db: Session = Depends(get_public_db)
):
    """Update tenant details"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Update fields
    if tenant_update.name is not None:
        tenant.name = tenant_update.name
    if tenant_update.is_active is not None:
        tenant.is_active = tenant_update.is_active
    if tenant_update.is_trial is not None:
        tenant.is_trial = tenant_update.is_trial

    db.commit()
    db.refresh(tenant)
    return tenant


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_public_db)
):
    """Delete tenant and all associated data"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    try:
        # Delete schema and all data
        TenantDatabaseManager.delete_tenant_schema(tenant.schema_name)

        # Delete tenant record
        db.delete(tenant)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tenant: {str(e)}"
        )

    return None
