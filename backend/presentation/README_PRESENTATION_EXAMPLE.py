"""
Presentation layer - API endpoints (FastAPI)

This layer:
- Handles HTTP requests/responses
- Validates input
- Calls use cases
- Returns responses
- Should be thin - just routing and serialization
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from application.README_APPLICATION_EXAMPLE import (
    LoginUseCase, LoginCommand, LoginResult,
    CreateTenantUseCase, CreateTenantCommand,
    UserNotFoundException, InvalidCredentialsException
)


# Request/Response Schemas (Pydantic)
class LoginRequest(BaseModel):
    """API request schema"""
    username: str
    password: str
    tenant_slug: str | None = None


class LoginResponse(BaseModel):
    """API response schema"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


class CreateTenantRequest(BaseModel):
    name: str
    slug: str
    admin_email: str
    admin_password: str


class CreateTenantResponse(BaseModel):
    tenant_id: int
    slug: str
    schema_name: str
    message: str


# API Router
router_v1 = APIRouter(prefix="/api/v1", tags=["Auth V1"])


# Dependency Injection
def get_login_use_case() -> LoginUseCase:
    """Factory for login use case with dependencies"""
    # In real app, these would come from DI container
    user_repository = ...  # Injected
    password_service = ...  # Injected
    token_service = ...    # Injected

    return LoginUseCase(user_repository, password_service, token_service)


def get_create_tenant_use_case() -> CreateTenantUseCase:
    """Factory for create tenant use case"""
    # All dependencies injected
    return CreateTenantUseCase(...)


# API Endpoints (Thin controllers)
@router_v1.post("/auth/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    use_case: LoginUseCase = Depends(get_login_use_case)
):
    """
    Login endpoint - Thin controller

    Benefits:
    - Just routing
    - No business logic
    - Easy to test
    - Clear separation of concerns
    """
    try:
        # Convert API request to use case command
        command = LoginCommand(
            username=request.username,
            password=request.password,
            tenant_slug=request.tenant_slug
        )

        # Execute use case
        result: LoginResult = await use_case.execute(command)

        # Convert use case result to API response
        return LoginResponse(
            access_token=result.access_token,
            user_id=result.user_id,
            username=result.username
        )

    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except InvalidCredentialsException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router_v1.post("/tenants", response_model=CreateTenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    request: CreateTenantRequest,
    use_case: CreateTenantUseCase = Depends(get_create_tenant_use_case)
):
    """Create tenant endpoint"""
    try:
        command = CreateTenantCommand(
            name=request.name,
            slug=request.slug,
            admin_email=request.admin_email,
            admin_password=request.admin_password
        )

        result = await use_case.execute(command)

        return CreateTenantResponse(
            tenant_id=result.tenant_id,
            slug=result.slug,
            schema_name=result.schema_name,
            message="Tenant created successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Exception Handlers (Centralized)
from fastapi import FastAPI

def register_exception_handlers(app: FastAPI):
    """Register global exception handlers"""

    @app.exception_handler(UserNotFoundException)
    async def user_not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "User not found"}
        )

    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_handler(request, exc):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"}
        )


# Comparison: Old vs New

"""
OLD (Current):
-------------
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
- Business logic in API route
- Direct database access
- Hard to test
- Violates single responsibility
- Can't reuse logic


NEW (Improved):
--------------
@router_v1.post("/auth/login")
async def login(request: LoginRequest, use_case: LoginUseCase = Depends()):
    command = LoginCommand(...)
    result = await use_case.execute(command)
    return LoginResponse(...)

BENEFITS:
- Thin controller
- Business logic in use case
- Easy to test (mock use case)
- Reusable (CLI, API, tests)
- Clear separation
- Follows SOLID principles
"""
