from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api import auth, repositories, analyses, settings as settings_api, tenants

# Import refactored auth v2
from app.api import auth_v2

# Import tenant middleware
from app.core.tenant_middleware import TenantMiddleware

# Import logging and error handling
from app.core.logging_config import setup_logging, get_logger
from app.core.error_handlers import register_exception_handlers

# Import security middleware
from app.core.security_middleware import (
    setup_security_middleware,
    setup_rate_limiting
)

# Import metrics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

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

# Setup security middleware (rate limiting, security headers, request size limits)
setup_security_middleware(app)
setup_rate_limiting(app)

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
    """
    Enhanced health check endpoint

    Checks:
    - Application status
    - Database connectivity
    - Multi-tenancy configuration

    Returns 200 if healthy, 503 if unhealthy
    """
    logger.debug("health_check_called")

    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "multi_tenancy": settings.ENABLE_MULTI_TENANCY,
        "checks": {}
    }

    # Check database connectivity
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        logger.error("health_check_database_failed", error=str(e))

    # Add timestamp
    health_status["timestamp"] = time.time()

    # Return 503 if unhealthy
    status_code = 200 if health_status["status"] == "healthy" else 503

    return Response(
        content=str(health_status),
        status_code=status_code,
        media_type="application/json"
    )


@app.get("/metrics")
def metrics():
    """
    Prometheus metrics endpoint

    Exposes metrics in Prometheus format for monitoring:
    - Request counts
    - Request durations
    - Error rates
    - Custom business metrics
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def validate_environment():
    """
    Validate critical environment variables at startup

    This ensures the application has all required configuration
    before starting to serve requests.
    """
    errors = []

    # Validate required settings
    if settings.SECRET_KEY == "your-secret-key-change-this-in-production":
        errors.append("SECRET_KEY is using default value - CHANGE THIS IN PRODUCTION!")

    if settings.JWT_SECRET_KEY == "your-jwt-secret-key-change-this-in-production":
        errors.append("JWT_SECRET_KEY is using default value - CHANGE THIS IN PRODUCTION!")

    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is not set")

    # Warn about production settings
    if not settings.DEBUG:
        logger.info("production_mode_enabled")
        if "localhost" in settings.DATABASE_URL or "127.0.0.1" in settings.DATABASE_URL:
            logger.warning("production_mode_with_local_database",
                          message="Running in production mode with local database")

    if errors:
        for error in errors:
            logger.error("environment_validation_error", error=error)
        raise RuntimeError(f"Environment validation failed: {errors}")

    logger.info("environment_validation_passed",
                debug=settings.DEBUG,
                multi_tenancy=settings.ENABLE_MULTI_TENANCY)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    # Validate environment first
    validate_environment()

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
