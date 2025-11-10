from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )

    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        is_active=True,
        is_admin=False  # First user should be made admin manually in DB
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and get access token

    In multi-tenant mode, tenant context is captured from:
    - Request state (set by middleware)
    - X-Tenant-Slug header
    - ?tenant= query parameter

    The tenant slug is embedded in the JWT token for automatic tenant routing.
    """
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Prepare token data
    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "is_admin": user.is_admin
    }

    # Include tenant information if in multi-tenant mode
    if settings.ENABLE_MULTI_TENANCY:
        from fastapi import Request
        from app.core.tenant_db import current_tenant_schema

        # Get tenant from current context
        schema = current_tenant_schema.get()
        if schema and schema != "public":
            # Extract tenant slug from schema name (tenant_acme -> acme)
            tenant_slug = schema.replace("tenant_", "")
            token_data["tenant_slug"] = tenant_slug
            token_data["tenant_schema"] = schema

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
