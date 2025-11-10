"""
Core exceptions for the application

This module defines the exception hierarchy and error codes.
All exceptions should inherit from these base classes.

Error Code Format: ERR_{DOMAIN}_{NUMBER}
- ERR_AUTH_001: Invalid credentials
- ERR_USER_001: User not found
- ERR_TENANT_001: Tenant not found
"""

from typing import Optional, Dict, Any


class BaseAppException(Exception):
    """Base exception for all application errors"""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dict for API response"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details
            }
        }


# Authentication & Authorization Exceptions
class AuthenticationException(BaseAppException):
    """Base authentication exception"""
    def __init__(self, message: str, error_code: str, details: Optional[Dict] = None):
        super().__init__(message, error_code, status_code=401, details=details)


class AuthorizationException(BaseAppException):
    """Base authorization exception"""
    def __init__(self, message: str, error_code: str, details: Optional[Dict] = None):
        super().__init__(message, error_code, status_code=403, details=details)


class InvalidCredentialsError(AuthenticationException):
    """Invalid username or password"""
    def __init__(self, details: Optional[Dict] = None):
        super().__init__(
            message="Invalid username or password",
            error_code="ERR_AUTH_001",
            details=details
        )


class InvalidTokenError(AuthenticationException):
    """Invalid or expired token"""
    def __init__(self, details: Optional[Dict] = None):
        super().__init__(
            message="Invalid or expired token",
            error_code="ERR_AUTH_002",
            details=details
        )


class InsufficientPermissionsError(AuthorizationException):
    """User doesn't have required permissions"""
    def __init__(self, required_permission: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Insufficient permissions. Required: {required_permission}",
            error_code="ERR_AUTH_003",
            details=details or {"required_permission": required_permission}
        )


# User Exceptions
class UserException(BaseAppException):
    """Base user exception"""
    pass


class UserNotFoundError(UserException):
    """User not found"""
    def __init__(self, identifier: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"User not found: {identifier}",
            error_code="ERR_USER_001",
            status_code=404,
            details=details or {"identifier": identifier}
        )


class UserAlreadyExistsError(UserException):
    """User with email/username already exists"""
    def __init__(self, field: str, value: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"User with {field} '{value}' already exists",
            error_code="ERR_USER_002",
            status_code=409,
            details=details or {"field": field, "value": value}
        )


class UserInactiveError(UserException):
    """User account is inactive"""
    def __init__(self, username: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"User account is inactive: {username}",
            error_code="ERR_USER_003",
            status_code=403,
            details=details or {"username": username}
        )


# Tenant Exceptions
class TenantException(BaseAppException):
    """Base tenant exception"""
    pass


class TenantNotFoundError(TenantException):
    """Tenant not found"""
    def __init__(self, identifier: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Tenant not found: {identifier}",
            error_code="ERR_TENANT_001",
            status_code=404,
            details=details or {"identifier": identifier}
        )


class TenantAlreadyExistsError(TenantException):
    """Tenant already exists"""
    def __init__(self, slug: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Tenant with slug '{slug}' already exists",
            error_code="ERR_TENANT_002",
            status_code=409,
            details=details or {"slug": slug}
        )


class TenantInactiveError(TenantException):
    """Tenant is inactive"""
    def __init__(self, slug: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Tenant is inactive: {slug}",
            error_code="ERR_TENANT_003",
            status_code=403,
            details=details or {"slug": slug}
        )


# Repository Exceptions
class RepositoryException(BaseAppException):
    """Base repository exception"""
    pass


class RepositoryNotFoundError(RepositoryException):
    """Repository not found"""
    def __init__(self, repo_id: int, details: Optional[Dict] = None):
        super().__init__(
            message=f"Repository not found: {repo_id}",
            error_code="ERR_REPO_001",
            status_code=404,
            details=details or {"repository_id": repo_id}
        )


class RepositoryAccessDeniedError(RepositoryException):
    """User doesn't have access to repository"""
    def __init__(self, repo_id: int, details: Optional[Dict] = None):
        super().__init__(
            message=f"Access denied to repository: {repo_id}",
            error_code="ERR_REPO_002",
            status_code=403,
            details=details or {"repository_id": repo_id}
        )


# Analysis Exceptions
class AnalysisException(BaseAppException):
    """Base analysis exception"""
    pass


class AnalysisNotFoundError(AnalysisException):
    """Analysis not found"""
    def __init__(self, analysis_id: int, details: Optional[Dict] = None):
        super().__init__(
            message=f"Analysis not found: {analysis_id}",
            error_code="ERR_ANALYSIS_001",
            status_code=404,
            details=details or {"analysis_id": analysis_id}
        )


class AnalysisFailedError(AnalysisException):
    """Analysis execution failed"""
    def __init__(self, reason: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Analysis failed: {reason}",
            error_code="ERR_ANALYSIS_002",
            status_code=500,
            details=details or {"reason": reason}
        )


# Validation Exceptions
class ValidationException(BaseAppException):
    """Base validation exception"""
    def __init__(self, message: str, field: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="ERR_VALIDATION_001",
            status_code=422,
            details=details or {"field": field}
        )


class InvalidInputError(ValidationException):
    """Invalid input provided"""
    def __init__(self, field: str, reason: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Invalid {field}: {reason}",
            field=field,
            details=details or {"field": field, "reason": reason}
        )


# Infrastructure Exceptions
class DatabaseException(BaseAppException):
    """Database error"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Database error: {message}",
            error_code="ERR_DB_001",
            status_code=500,
            details=details
        )


class ExternalServiceException(BaseAppException):
    """External service error (GitHub, LLM, etc.)"""
    def __init__(self, service: str, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"{service} error: {message}",
            error_code="ERR_EXTERNAL_001",
            status_code=502,
            details=details or {"service": service}
        )
