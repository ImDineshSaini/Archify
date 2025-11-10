"""
Security Middleware and Rate Limiting

This module provides:
- Rate limiting for API endpoints
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Request size limits
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import FastAPI, status
from typing import Callable
import time

from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Default: 100 requests per minute
    storage_uri="memory://",  # In production, use Redis: "redis://localhost:6379"
    strategy="fixed-window"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses

    Security headers:
    - X-Content-Type-Options: Prevent MIME type sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable XSS filter
    - Strict-Transport-Security: Enforce HTTPS
    - Content-Security-Policy: Prevent XSS and injection attacks
    - X-Permitted-Cross-Domain-Policies: Restrict cross-domain policies
    - Referrer-Policy: Control referrer information
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HSTS (HTTP Strict Transport Security) - only in production with HTTPS
        # Commented out for local development
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy - restrictive policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp_policy

        # Add custom security header with app version
        response.headers["X-Security-Version"] = "1.0"

        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit request body size

    This prevents DoS attacks via large payloads.
    Default limit: 10MB
    """

    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check Content-Length header
        if "content-length" in request.headers:
            content_length = int(request.headers["content-length"])
            if content_length > self.max_size:
                logger.warning(
                    "request_too_large",
                    content_length=content_length,
                    max_size=self.max_size,
                    path=request.url.path
                )
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "error": {
                            "code": "ERR_REQUEST_TOO_LARGE",
                            "message": f"Request body too large. Maximum size: {self.max_size / 1024 / 1024}MB",
                            "details": {
                                "max_size_bytes": self.max_size,
                                "received_bytes": content_length
                            }
                        }
                    }
                )

        return await call_next(request)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request timing and add timing headers

    This helps with performance monitoring and debugging.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # Log slow requests (> 1 second)
        if process_time > 1.0:
            logger.warning(
                "slow_request",
                path=request.url.path,
                method=request.method,
                duration_seconds=process_time
            )

        return response


def setup_rate_limiting(app: FastAPI):
    """
    Setup rate limiting for FastAPI application

    This function:
    - Adds rate limiter to app state
    - Registers exception handler for rate limit errors
    - Configures default and endpoint-specific limits
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    logger.info("rate_limiting_enabled", default_limit="100/minute")


def setup_security_middleware(app: FastAPI):
    """
    Setup all security middleware for FastAPI application

    This includes:
    - Security headers middleware
    - Request size limit middleware
    - Request timing middleware
    """
    # Add middlewares in reverse order (they're applied in LIFO order)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)  # 10MB
    app.add_middleware(SecurityHeadersMiddleware)

    logger.info("security_middleware_enabled",
                features=["security_headers", "request_size_limits", "request_timing"])


# Rate limit decorators for specific use cases
AUTH_RATE_LIMIT = "5/minute"  # 5 login attempts per minute
REGISTER_RATE_LIMIT = "3/minute"  # 3 registration attempts per minute
API_RATE_LIMIT = "60/minute"  # 60 API calls per minute for authenticated users
