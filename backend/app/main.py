from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, repositories, analyses, settings as settings_api, tenants

# Import refactored auth v2
from app.api import auth_v2

# Import tenant middleware
from app.core.tenant_middleware import TenantMiddleware

# Import logging and error handling
from app.core.logging_config import setup_logging, get_logger
from app.core.error_handlers import register_exception_handlers

# Setup logging
setup_logging(
    json_logs=not settings.DEBUG,  # JSON in production, pretty in development
    log_level="DEBUG" if settings.DEBUG else "INFO"
)

logger = get_logger(__name__)

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
    logger.info("multi_tenancy_enabled", status="active")
else:
    logger.info("multi_tenancy_disabled", status="inactive")

# Register exception handlers (IMPORTANT!)
register_exception_handlers(app)
logger.info("exception_handlers_registered")

# Include routers
app.include_router(tenants.router, prefix="/api")  # Tenant management (always available)
app.include_router(auth.router, prefix="/api")      # Old auth (v1)
app.include_router(auth_v2.router, prefix="/api/v2") # New auth (v2) - REFACTORED!
app.include_router(repositories.router, prefix="/api")
app.include_router(analyses.router, prefix="/api")
app.include_router(settings_api.router, prefix="/api")

logger.info("application_started", app_name=settings.APP_NAME, version=settings.APP_VERSION)


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
    logger.debug("health_check_called")
    return {
        "status": "healthy",
        "multi_tenancy": settings.ENABLE_MULTI_TENANCY
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(
        "application_startup",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        multi_tenancy=settings.ENABLE_MULTI_TENANCY
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("application_shutdown")
