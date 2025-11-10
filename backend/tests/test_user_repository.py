"""
Unit tests for UserRepository

These tests verify the repository layer works correctly:
- Data access operations
- Error handling
- Database interactions
"""

import pytest
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.exceptions import DatabaseException, UserNotFoundError
from app.core.security import get_password_hash, verify_password


@pytest.mark.unit
class TestUserRepository:
    """Test suite for UserRepository"""

    def test_find_by_id_existing_user(self, test_db: Session, test_user: User):
        """Test finding user by ID when user exists"""
        repo = UserRepository(test_db)

        # Act
        found_user = repo.find_by_id(test_user.id)

        # Assert
        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.username == test_user.username
        assert found_user.email == test_user.email

    def test_find_by_id_nonexistent_user(self, test_db: Session):
        """Test finding user by ID when user doesn't exist"""
        repo = UserRepository(test_db)

        # Act
        found_user = repo.find_by_id(99999)

        # Assert
        assert found_user is None

    def test_find_by_username_existing(self, test_db: Session, test_user: User):
        """Test finding user by username when user exists"""
        repo = UserRepository(test_db)

        # Act
        found_user = repo.find_by_username("testuser")

        # Assert
        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.username == "testuser"

    def test_find_by_username_nonexistent(self, test_db: Session):
        """Test finding user by username when user doesn't exist"""
        repo = UserRepository(test_db)

        # Act
        found_user = repo.find_by_username("nonexistent_user")

        # Assert
        assert found_user is None

    def test_find_by_email_existing(self, test_db: Session, test_user: User):
        """Test finding user by email when user exists"""
        repo = UserRepository(test_db)

        # Act
        found_user = repo.find_by_email("test@example.com")

        # Assert
        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.email == "test@example.com"

    def test_find_by_email_nonexistent(self, test_db: Session):
        """Test finding user by email when user doesn't exist"""
        repo = UserRepository(test_db)

        # Act
        found_user = repo.find_by_email("nonexistent@example.com")

        # Assert
        assert found_user is None

    def test_find_by_username_or_email_with_username(self, test_db: Session, test_user: User):
        """Test finding user by username when using username_or_email"""
        repo = UserRepository(test_db)

        # Act
        found_user = repo.find_by_username_or_email("testuser")

        # Assert
        assert found_user is not None
        assert found_user.id == test_user.id

    def test_find_by_username_or_email_with_email(self, test_db: Session, test_user: User):
        """Test finding user by email when using username_or_email"""
        repo = UserRepository(test_db)

        # Act
        found_user = repo.find_by_username_or_email("test@example.com")

        # Assert
        assert found_user is not None
        assert found_user.id == test_user.id

    def test_create_user_success(self, test_db: Session):
        """Test creating a new user successfully"""
        repo = UserRepository(test_db)

        # Arrange
        new_user = User(
            username="newuser",
            email="newuser@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="New User",
            is_active=True,
            is_admin=False
        )

        # Act
        created_user = repo.create(new_user)

        # Assert
        assert created_user.id is not None
        assert created_user.username == "newuser"
        assert created_user.email == "newuser@example.com"
        assert created_user.full_name == "New User"
        assert created_user.is_active is True
        assert created_user.is_admin is False

        # Verify it's in database
        found_user = repo.find_by_id(created_user.id)
        assert found_user is not None
        assert found_user.username == "newuser"

    def test_create_user_with_duplicate_username(self, test_db: Session, test_user: User):
        """Test creating user with duplicate username raises exception"""
        repo = UserRepository(test_db)

        # Arrange - try to create user with same username
        duplicate_user = User(
            username="testuser",  # Same as test_user
            email="different@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Duplicate User",
            is_active=True,
            is_admin=False
        )

        # Act & Assert
        with pytest.raises(DatabaseException):
            repo.create(duplicate_user)

    def test_update_user_success(self, test_db: Session, test_user: User):
        """Test updating user successfully"""
        repo = UserRepository(test_db)

        # Arrange
        test_user.full_name = "Updated Name"
        test_user.email = "updated@example.com"

        # Act
        updated_user = repo.update(test_user)

        # Assert
        assert updated_user.full_name == "Updated Name"
        assert updated_user.email == "updated@example.com"

        # Verify in database
        found_user = repo.find_by_id(test_user.id)
        assert found_user.full_name == "Updated Name"
        assert found_user.email == "updated@example.com"

    def test_update_nonexistent_user(self, test_db: Session):
        """Test updating non-existent user raises error"""
        repo = UserRepository(test_db)

        # Arrange
        nonexistent_user = User(
            id=99999,
            username="nonexistent",
            email="nonexistent@example.com",
            hashed_password="hash",
            is_active=True,
            is_admin=False
        )

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            repo.update(nonexistent_user)

    def test_delete_user_success(self, test_db: Session, test_user: User):
        """Test deleting user successfully"""
        repo = UserRepository(test_db)

        # Act
        result = repo.delete(test_user.id)

        # Assert
        assert result is True

        # Verify user is deleted
        found_user = repo.find_by_id(test_user.id)
        assert found_user is None

    def test_delete_nonexistent_user(self, test_db: Session):
        """Test deleting non-existent user returns False"""
        repo = UserRepository(test_db)

        # Act
        result = repo.delete(99999)

        # Assert
        assert result is False

    def test_exists_with_username_true(self, test_db: Session, test_user: User):
        """Test exists returns True when username exists"""
        repo = UserRepository(test_db)

        # Act
        result = repo.exists(username="testuser")

        # Assert
        assert result is True

    def test_exists_with_username_false(self, test_db: Session):
        """Test exists returns False when username doesn't exist"""
        repo = UserRepository(test_db)

        # Act
        result = repo.exists(username="nonexistent")

        # Assert
        assert result is False

    def test_exists_with_email_true(self, test_db: Session, test_user: User):
        """Test exists returns True when email exists"""
        repo = UserRepository(test_db)

        # Act
        result = repo.exists(email="test@example.com")

        # Assert
        assert result is True

    def test_exists_with_email_false(self, test_db: Session):
        """Test exists returns False when email doesn't exist"""
        repo = UserRepository(test_db)

        # Act
        result = repo.exists(email="nonexistent@example.com")

        # Assert
        assert result is False

    def test_exists_with_both_username_and_email(self, test_db: Session, test_user: User):
        """Test exists with both username and email"""
        repo = UserRepository(test_db)

        # Act
        result = repo.exists(username="testuser", email="test@example.com")

        # Assert
        assert result is True

    def test_multiple_users_no_interference(self, test_db: Session, multiple_users: list[User]):
        """Test that multiple users don't interfere with each other"""
        repo = UserRepository(test_db)

        # Act & Assert - each user should be findable
        for user in multiple_users:
            found_user = repo.find_by_id(user.id)
            assert found_user is not None
            assert found_user.id == user.id
            assert found_user.username == user.username

    def test_repository_isolation(self, test_db: Session, test_user: User):
        """Test that repository instances share the same database session"""
        repo1 = UserRepository(test_db)
        repo2 = UserRepository(test_db)

        # Act - create user with repo1
        new_user = User(
            username="shared_user",
            email="shared@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_admin=False
        )
        created_user = repo1.create(new_user)

        # Assert - should be accessible via repo2
        found_user = repo2.find_by_id(created_user.id)
        assert found_user is not None
        assert found_user.username == "shared_user"
