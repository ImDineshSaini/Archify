from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from app.core.database import Base


class Tenant(Base):
    """
    Tenant model - stored in public schema
    Each tenant represents an organization with isolated data
    """
    __tablename__ = "tenants"
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Organization name
    slug = Column(String, unique=True, index=True, nullable=False)  # URL-safe identifier
    schema_name = Column(String, unique=True, nullable=False)  # PostgreSQL schema name

    # Contact info
    admin_email = Column(String, nullable=False)
    admin_name = Column(String)

    # Status
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=True)
    trial_ends_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Custom settings (JSON stored as text)
    settings = Column(Text)  # JSON string for tenant-specific settings
