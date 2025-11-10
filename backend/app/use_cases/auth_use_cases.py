"""
Authentication Use Cases - Business logic for authentication

These use cases encapsulate the business logic for authentication operations.
Benefits:
- Testable without HTTP layer
- Reusable across different interfaces (API, CLI, tests)
- Clear business logic
- Easy to mock dependencies
"""

from dataclasses import dataclass
from typing import Optional
from datetime import timedelta

from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserInactiveError,
    UserAlreadyExistsError
)
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


# Input/Output DTOs (Data Transfer Objects)
@dataclass
class LoginCommand:
    """Input for login use case"""
    username: str
    password: str
    tenant_slug: Optional[str] = None


@dataclass
class LoginResult:
    """Output from login use case"""
    access_token: str
    token_type: str
    user_id: int
    username: str
    is_admin: bool


@dataclass
class RegisterCommand:
    """Input for register use case"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


@dataclass
class RegisterResult:
    """Output from register use case"""
    user_id: int
    username: str
    email: str
    message: str


class LoginUseCase:
    """
    Login Use Case - Handles user authentication

    This use case:
    1. Validates credentials
    2. Checks user status
    3. Generates JWT token
    4. Logs the login attempt

    Benefits:
    - Testable without HTTP
    - Clear business logic
    - Easy to add features (2FA, rate limiting, etc.)
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, command: LoginCommand) -> LoginResult:
        """
        Execute login use case

        Args:
            command: Login command with credentials

        Returns:
            LoginResult with access token

        Raises:
            InvalidCredentialsError: If credentials are invalid
            UserInactiveError: If user account is inactive
        """
        logger.info("login_attempt", username=command.username)

        # 1. Find user
        user = self.user_repository.find_by_username(command.username)
        if not user:
            logger.warning("login_failed_user_not_found", username=command.username)
            raise InvalidCredentialsError(
                details={"username": command.username}
            )

        # 2. Verify password
        if not verify_password(command.password, user.hashed_password):
            logger.warning(
                "login_failed_invalid_password",
                username=command.username,
                user_id=user.id
            )
            raise InvalidCredentialsError(
                details={"username": command.username}
            )

        # 3. Check if user is active
        if not user.is_active:
            logger.warning(
                "login_failed_inactive_user",
                username=command.username,
                user_id=user.id
            )
            raise UserInactiveError(
                username=command.username,
                details={"user_id": user.id}
            )

        # 4. Generate token
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "is_admin": user.is_admin
        }

        # Include tenant information if provided
        if command.tenant_slug:
            token_data["tenant_slug"] = command.tenant_slug
            token_data["tenant_schema"] = f"tenant_{command.tenant_slug}"

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )

        # 5. Log successful login
        logger.info(
            "login_successful",
            user_id=user.id,
            username=user.username,
            is_admin=user.is_admin,
            tenant_slug=command.tenant_slug
        )

        # 6. Return result
        return LoginResult(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            username=user.username,
            is_admin=user.is_admin
        )


class RegisterUseCase:
    """
    Register Use Case - Handles user registration

    This use case:
    1. Validates input
    2. Checks for existing users
    3. Creates new user
    4. Logs the registration
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, command: RegisterCommand) -> RegisterResult:
        """
        Execute register use case

        Args:
            command: Registration command

        Returns:
            RegisterResult with user info

        Raises:
            UserAlreadyExistsError: If username or email already exists
        """
        logger.info(
            "registration_attempt",
            username=command.username,
            email=command.email
        )

        # 1. Check if username already exists
        if self.user_repository.exists(username=command.username):
            logger.warning(
                "registration_failed_username_exists",
                username=command.username
            )
            raise UserAlreadyExistsError(
                field="username",
                value=command.username
            )

        # 2. Check if email already exists
        if self.user_repository.exists(email=command.email):
            logger.warning(
                "registration_failed_email_exists",
                email=command.email
            )
            raise UserAlreadyExistsError(
                field="email",
                value=command.email
            )

        # 3. Create user
        from app.models.user import User

        user = User(
            username=command.username,
            email=command.email,
            hashed_password=get_password_hash(command.password),
            full_name=command.full_name,
            is_active=True,
            is_admin=False
        )

        created_user = self.user_repository.create(user)

        # 4. Log successful registration
        logger.info(
            "registration_successful",
            user_id=created_user.id,
            username=created_user.username,
            email=created_user.email
        )

        # 5. Return result
        return RegisterResult(
            user_id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            message="User registered successfully"
        )
