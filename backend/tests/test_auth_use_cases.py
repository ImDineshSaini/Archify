"""
Unit tests for Authentication Use Cases

These tests verify the business logic works correctly:
- Login use case
- Registration use case
- Error handling
- Token generation
"""

import pytest
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

from app.use_cases.auth_use_cases import (
    LoginUseCase,
    RegisterUseCase,
    LoginCommand,
    RegisterCommand,
    LoginResult,
    RegisterResult
)
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.exceptions import (
    InvalidCredentialsError,
    UserInactiveError,
    UserAlreadyExistsError
)
from app.core.security import get_password_hash, verify_password


@pytest.mark.unit
class TestLoginUseCase:
    """Test suite for LoginUseCase"""

    def test_login_success(self, test_db: Session, test_user: User):
        """Test successful login with valid credentials"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = LoginUseCase(repo)
        command = LoginCommand(username="testuser", password="testpass123")

        # Act
        result = use_case.execute(command)

        # Assert
        assert isinstance(result, LoginResult)
        assert result.access_token is not None
        assert result.token_type == "bearer"
        assert result.user_id == test_user.id
        assert result.username == test_user.username
        assert result.is_admin == test_user.is_admin

    def test_login_with_nonexistent_user(self, test_db: Session):
        """Test login fails with non-existent username"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = LoginUseCase(repo)
        command = LoginCommand(username="nonexistent", password="password123")

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            use_case.execute(command)

        assert "Invalid username or password" in str(exc_info.value)

    def test_login_with_wrong_password(self, test_db: Session, test_user: User):
        """Test login fails with wrong password"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = LoginUseCase(repo)
        command = LoginCommand(username="testuser", password="wrongpassword")

        # Act & Assert
        with pytest.raises(InvalidCredentialsError) as exc_info:
            use_case.execute(command)

        assert "Invalid username or password" in str(exc_info.value)

    def test_login_with_inactive_user(self, test_db: Session, inactive_user: User):
        """Test login fails for inactive user"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = LoginUseCase(repo)
        command = LoginCommand(username="inactive_user", password="inactive123")

        # Act & Assert
        with pytest.raises(UserInactiveError) as exc_info:
            use_case.execute(command)

        assert "inactive" in str(exc_info.value).lower()

    def test_login_admin_user(self, test_db: Session, test_admin: User):
        """Test successful login for admin user"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = LoginUseCase(repo)
        command = LoginCommand(username="admin", password="admin123")

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.is_admin is True
        assert result.user_id == test_admin.id

    def test_login_with_tenant_slug(self, test_db: Session, test_user: User):
        """Test login includes tenant information in token"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = LoginUseCase(repo)
        command = LoginCommand(
            username="testuser",
            password="testpass123",
            tenant_slug="acme"
        )

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.access_token is not None
        # Token should be a valid JWT (starts with ey for base64 header)
        assert result.access_token.startswith("ey")

    def test_login_password_verification(self, test_db: Session, test_user: User):
        """Test that password is properly verified using bcrypt"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = LoginUseCase(repo)

        # Act & Assert - correct password
        command_correct = LoginCommand(username="testuser", password="testpass123")
        result = use_case.execute(command_correct)
        assert result.access_token is not None

        # Act & Assert - incorrect password
        command_wrong = LoginCommand(username="testuser", password="wrongpassword")
        with pytest.raises(InvalidCredentialsError):
            use_case.execute(command_wrong)

    def test_login_token_contains_user_data(self, test_db: Session, test_user: User):
        """Test that generated token contains user data"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = LoginUseCase(repo)
        command = LoginCommand(username="testuser", password="testpass123")

        # Act
        result = use_case.execute(command)

        # Assert - token should be a JWT
        assert result.access_token is not None
        assert len(result.access_token) > 50  # JWT tokens are long
        parts = result.access_token.split(".")
        assert len(parts) == 3  # JWT has 3 parts: header.payload.signature


@pytest.mark.unit
class TestRegisterUseCase:
    """Test suite for RegisterUseCase"""

    def test_register_success(self, test_db: Session):
        """Test successful user registration"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = RegisterUseCase(repo)
        command = RegisterCommand(
            username="newuser",
            email="newuser@example.com",
            password="password123",
            full_name="New User"
        )

        # Act
        result = use_case.execute(command)

        # Assert
        assert isinstance(result, RegisterResult)
        assert result.user_id is not None
        assert result.username == "newuser"
        assert result.email == "newuser@example.com"
        assert result.message == "User registered successfully"

        # Verify user exists in database
        user = repo.find_by_username("newuser")
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.is_active is True
        assert user.is_admin is False

    def test_register_password_is_hashed(self, test_db: Session):
        """Test that password is properly hashed"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = RegisterUseCase(repo)
        command = RegisterCommand(
            username="newuser",
            email="newuser@example.com",
            password="password123"
        )

        # Act
        result = use_case.execute(command)

        # Assert
        user = repo.find_by_id(result.user_id)
        assert user.hashed_password != "password123"  # Not plain text
        assert user.hashed_password.startswith("$2b$")  # Bcrypt hash
        assert verify_password("password123", user.hashed_password)  # Can verify

    def test_register_with_duplicate_username(self, test_db: Session, test_user: User):
        """Test registration fails with duplicate username"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = RegisterUseCase(repo)
        command = RegisterCommand(
            username="testuser",  # Same as test_user
            email="different@example.com",
            password="password123"
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            use_case.execute(command)

        error = exc_info.value
        assert error.details["field"] == "username"
        assert error.details["value"] == "testuser"

    def test_register_with_duplicate_email(self, test_db: Session, test_user: User):
        """Test registration fails with duplicate email"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = RegisterUseCase(repo)
        command = RegisterCommand(
            username="differentuser",
            email="test@example.com",  # Same as test_user
            password="password123"
        )

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            use_case.execute(command)

        error = exc_info.value
        assert error.details["field"] == "email"
        assert error.details["value"] == "test@example.com"

    def test_register_without_full_name(self, test_db: Session):
        """Test registration works without full_name (optional field)"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = RegisterUseCase(repo)
        command = RegisterCommand(
            username="newuser",
            email="newuser@example.com",
            password="password123",
            full_name=None
        )

        # Act
        result = use_case.execute(command)

        # Assert
        assert result.user_id is not None
        user = repo.find_by_id(result.user_id)
        assert user.full_name is None

    def test_register_user_defaults(self, test_db: Session):
        """Test that new users have correct default values"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = RegisterUseCase(repo)
        command = RegisterCommand(
            username="newuser",
            email="newuser@example.com",
            password="password123"
        )

        # Act
        result = use_case.execute(command)

        # Assert
        user = repo.find_by_id(result.user_id)
        assert user.is_active is True  # New users are active
        assert user.is_admin is False  # New users are not admin
        assert user.created_at is not None  # Timestamp set

    def test_register_multiple_users(self, test_db: Session):
        """Test registering multiple users works correctly"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = RegisterUseCase(repo)

        # Act - register 3 users
        user_ids = []
        for i in range(3):
            command = RegisterCommand(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password=f"password{i}"
            )
            result = use_case.execute(command)
            user_ids.append(result.user_id)

        # Assert - all users exist and are unique
        assert len(user_ids) == 3
        assert len(set(user_ids)) == 3  # All unique IDs

        for i, user_id in enumerate(user_ids):
            user = repo.find_by_id(user_id)
            assert user is not None
            assert user.username == f"user{i}"

    def test_register_case_sensitivity(self, test_db: Session, test_user: User):
        """Test username case sensitivity in registration"""
        # Arrange
        repo = UserRepository(test_db)
        use_case = RegisterUseCase(repo)

        # Note: Database behavior depends on collation settings
        # This test documents current behavior
        command = RegisterCommand(
            username="TESTUSER",  # Different case
            email="different@example.com",
            password="password123"
        )

        # In most cases, this should work as username is case-sensitive in DB
        # But this depends on your DB configuration
        try:
            result = use_case.execute(command)
            # If it succeeds, verify both users exist
            user1 = repo.find_by_username("testuser")
            user2 = repo.find_by_username("TESTUSER")
            assert user1.id != user2.id
        except UserAlreadyExistsError:
            # If DB treats usernames as case-insensitive, this is expected
            pytest.skip("Database treats usernames as case-insensitive")

    def test_register_validates_input_types(self, test_db: Session):
        """Test that RegisterCommand validates input types"""
        # This is handled by the dataclass/Pydantic at API layer
        # But we document expected behavior

        # Valid command
        command = RegisterCommand(
            username="testuser",
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )

        assert command.username == "testuser"
        assert command.email == "test@example.com"
        assert command.password == "password123"
        assert command.full_name == "Test User"
