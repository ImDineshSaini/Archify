from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, repositories, analyses, settings as settings_api, tenants

# Import tenant middleware
from app.core.tenant_middleware import TenantMiddleware

# Create database tables in public schema
Base.metadata.create_all(bind=engine)

# Also ensure tenant table exists in public schema
from app.models.tenant import Tenant
Tenant.__table__.create(bind=engine, checkfirst=True)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered code analysis platform with multi-tenancy support"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant middleware if multi-tenancy is enabled
if settings.ENABLE_MULTI_TENANCY:
    app.add_middleware(TenantMiddleware)

# Include routers
app.include_router(tenants.router, prefix="/api")  # Tenant management (always available)
app.include_router(auth.router, prefix="/api")
app.include_router(repositories.router, prefix="/api")
app.include_router(analyses.router, prefix="/api")
app.include_router(settings_api.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "multi_tenancy": settings.ENABLE_MULTI_TENANCY,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "multi_tenancy": settings.ENABLE_MULTI_TENANCY
    }
