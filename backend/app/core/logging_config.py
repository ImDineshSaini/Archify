"""
Logging configuration for the application

Uses structlog for structured, contextual logging.
All logs include request_id, user_id, tenant_slug when available.
"""

import logging
import sys
from typing import Any, Dict
from contextvars import ContextVar

import structlog
from structlog.types import EventDict, Processor

# Context variables for request tracking
request_id_ctx: ContextVar[str] = ContextVar('request_id', default='')
user_id_ctx: ContextVar[int] = ContextVar('user_id', default=0)
tenant_slug_ctx: ContextVar[str] = ContextVar('tenant_slug', default='')


def add_context_processor(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add context variables to all log entries

    Adds:
    - request_id: Unique ID for each request
    - user_id: Current authenticated user ID
    - tenant_slug: Current tenant context
    """
    request_id = request_id_ctx.get()
    if request_id:
        event_dict['request_id'] = request_id

    user_id = user_id_ctx.get()
    if user_id:
        event_dict['user_id'] = user_id

    tenant_slug = tenant_slug_ctx.get()
    if tenant_slug:
        event_dict['tenant'] = tenant_slug

    return event_dict


def setup_logging(json_logs: bool = False, log_level: str = "INFO"):
    """
    Configure structured logging

    Args:
        json_logs: If True, output JSON logs (for production)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_context_processor,
    ]

    if json_logs:
        # Production: JSON logs
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        # Development: Pretty console logs
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a logger instance

    Usage:
        logger = get_logger(__name__)
        logger.info("user_login", username="john", success=True)
        logger.error("auth_failed", username="jane", reason="invalid_password")
    """
    return structlog.get_logger(name)


# Convenience functions for setting context
def set_request_id(request_id: str):
    """Set request ID for current context"""
    request_id_ctx.set(request_id)


def set_user_id(user_id: int):
    """Set user ID for current context"""
    user_id_ctx.set(user_id)


def set_tenant_slug(tenant_slug: str):
    """Set tenant slug for current context"""
    tenant_slug_ctx.set(tenant_slug)


def clear_context():
    """Clear all context variables"""
    request_id_ctx.set('')
    user_id_ctx.set(0)
    tenant_slug_ctx.set('')


# Example log messages for documentation
"""
LOGGING EXAMPLES:

1. Simple Info Log:
    logger.info("user_registered", user_id=123, email="user@example.com")
    Output: {"event": "user_registered", "user_id": 123, "email": "user@example.com", "timestamp": "..."}

2. Error with Exception:
    try:
        risky_operation()
    except Exception as e:
        logger.error("operation_failed", error=str(e), exc_info=True)

3. With Context:
    set_request_id("req-123")
    set_user_id(456)
    logger.info("analysis_started", repository_id=789)
    # Automatically includes request_id and user_id

4. Performance Tracking:
    import time
    start = time.time()
    result = expensive_operation()
    logger.info(
        "operation_completed",
        duration_ms=(time.time() - start) * 1000,
        result_count=len(result)
    )

5. Structured Data:
    logger.info(
        "api_request",
        method="POST",
        path="/api/v1/repositories",
        status_code=201,
        response_time_ms=123
    )
"""
