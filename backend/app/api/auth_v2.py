"""
Authentication API v2 - Refactored with clean architecture

This version uses:
- Repository pattern for data access
- Use cases for business logic
- Proper exception handling
- Structured logging
- Clear separation of concerns

Compare this to the old auth.py to see the improvements!
"""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.use_cases.auth_use_cases import (
    LoginUseCase,
    RegisterUseCase,
    LoginCommand,
    RegisterCommand
)
from app.core.logging_config import get_logger, set_request_id, set_user_id, set_tenant_slug
from app.core.tenant_db import current_tenant_schema
from app.core.config import settings
import uuid

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication V2"])


# Request/Response Schemas (API Layer)
class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "securepassword123"
            }
        }


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    is_admin: bool

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": 1,
                "username": "john_doe",
                "is_admin": False
            }
        }


class RegisterRequest(BaseModel):
    """Registration request schema"""
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "securepassword123",
                "full_name": "John Doe"
            }
        }


class RegisterResponse(BaseModel):
    """Registration response schema"""
    user_id: int
    username: str
    email: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "message": "User registered successfully"
            }
        }


# Dependency Injection
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Factory for user repository"""
    return UserRepository(db)


def get_login_use_case(
    user_repository: UserRepository = Depends(get_user_repository)
) -> LoginUseCase:
    """Factory for login use case"""
    return LoginUseCase(user_repository)


def get_register_use_case(
    user_repository: UserRepository = Depends(get_user_repository)
) -> RegisterUseCase:
    """Factory for register use case"""
    return RegisterUseCase(user_repository)


# API Endpoints (Thin Controllers)
@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(
    request: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case)
):
    """
    Login endpoint

    **This is a THIN controller** - it only:
    1. Receives HTTP request
    2. Sets up logging context
    3. Converts request to command
    4. Calls use case
    5. Converts result to response
    6. Returns HTTP response

    All business logic is in the use case!

    **Error Responses:**

    - 401 Unauthorized:
      ```json
      {
        "error": {
          "code": "ERR_AUTH_001",
          "message": "Invalid username or password",
          "details": {"username": "john_doe"}
        }
      }
      ```

    - 403 Forbidden:
      ```json
      {
        "error": {
          "code": "ERR_USER_003",
          "message": "User account is inactive: john_doe",
          "details": {"username": "john_doe"}
        }
      }
      ```
    """
    # Set request ID for logging
    request_id = str(uuid.uuid4())
    set_request_id(request_id)

    # Get tenant context if in multi-tenant mode
    tenant_slug = None
    if settings.ENABLE_MULTI_TENANCY:
        schema = current_tenant_schema.get()
        if schema and schema != "public":
            tenant_slug = schema.replace("tenant_", "")
            set_tenant_slug(tenant_slug)

    # Convert API request to use case command
    command = LoginCommand(
        username=request.username,
        password=request.password,
        tenant_slug=tenant_slug
    )

    # Execute use case
    result = use_case.execute(command)

    # Set user context for subsequent logs
    set_user_id(result.user_id)

    # Convert use case result to API response
    return LoginResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        user_id=result.user_id,
        username=result.username,
        is_admin=result.is_admin
    )


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    use_case: RegisterUseCase = Depends(get_register_use_case)
):
    """
    Register a new user

    **Error Responses:**

    - 409 Conflict (Username exists):
      ```json
      {
        "error": {
          "code": "ERR_USER_002",
          "message": "User with username 'john_doe' already exists",
          "details": {"field": "username", "value": "john_doe"}
        }
      }
      ```

    - 409 Conflict (Email exists):
      ```json
      {
        "error": {
          "code": "ERR_USER_002",
          "message": "User with email 'john@example.com' already exists",
          "details": {"field": "email", "value": "john@example.com"}
        }
      }
      ```

    - 422 Unprocessable Entity (Validation error):
      ```json
      {
        "error": {
          "code": "ERR_VALIDATION_001",
          "message": "Validation error",
          "details": {
            "validation_errors": [
              {
                "field": "email",
                "message": "value is not a valid email address",
                "type": "value_error.email"
              }
            ]
          }
        }
      }
      ```
    """
    # Set request ID for logging
    request_id = str(uuid.uuid4())
    set_request_id(request_id)

    # Convert API request to use case command
    command = RegisterCommand(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )

    # Execute use case
    result = use_case.execute(command)

    # Convert use case result to API response
    return RegisterResponse(
        user_id=result.user_id,
        username=result.username,
        email=result.email,
        message=result.message
    )


# Comparison with old code:
"""
OLD CODE (auth.py):
------------------
@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(...)
    if not user.is_active:
        raise HTTPException(...)
    access_token = create_access_token(...)
    return {"access_token": access_token}

PROBLEMS:
- 50 lines of mixed concerns
- Business logic in controller
- Direct database access
- Hard to test
- No logging
- Inconsistent error responses


NEW CODE (auth_v2.py):
---------------------
@router.post("/login")
def login(request: LoginRequest, use_case: LoginUseCase = Depends()):
    command = LoginCommand(...)
    result = use_case.execute(command)
    return LoginResponse(...)

BENEFITS:
- 10 lines per endpoint
- Thin controller (just routing)
- Business logic in use case
- Repository handles data access
- Easy to test (mock use case)
- Structured logging throughout
- Consistent error responses with error codes
- Clear API documentation
- Reusable use cases (API, CLI, tests)
"""
