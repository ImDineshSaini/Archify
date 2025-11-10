from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class TenantCreate(BaseModel):
    name: str
    slug: str
    admin_email: EmailStr
    admin_name: Optional[str] = None
    admin_password: str


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    is_trial: Optional[bool] = None


class TenantResponse(BaseModel):
    id: int
    name: str
    slug: str
    schema_name: str
    admin_email: str
    admin_name: Optional[str]
    is_active: bool
    is_trial: bool
    trial_ends_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
