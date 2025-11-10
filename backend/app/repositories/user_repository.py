"""
User Repository - Data access layer for User entity

This repository encapsulates all database operations for users.
Benefits:
- Easy to test (can mock)
- Easy to switch database implementation
- Centralized query logic
- Domain layer doesn't know about SQLAlchemy
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.core.exceptions import UserNotFoundError, DatabaseException
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class UserRepository:
    """Repository for User entity"""

    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Find user by ID

        Args:
            user_id: User ID

        Returns:
            User object or None

        Raises:
            DatabaseException: If database error occurs
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                logger.debug("user_found_by_id", user_id=user_id)
            return user
        except Exception as e:
            logger.error("database_error_find_by_id", user_id=user_id, error=str(e))
            raise DatabaseException(f"Failed to find user by ID: {str(e)}")

    def find_by_username(self, username: str) -> Optional[User]:
        """
        Find user by username

        Args:
            username: Username to search for

        Returns:
            User object or None

        Raises:
            DatabaseException: If database error occurs
        """
        try:
            user = self.db.query(User).filter(User.username == username).first()
            if user:
                logger.debug("user_found_by_username", username=username, user_id=user.id)
            return user
        except Exception as e:
            logger.error("database_error_find_by_username", username=username, error=str(e))
            raise DatabaseException(f"Failed to find user by username: {str(e)}")

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        try:
            user = self.db.query(User).filter(User.email == email).first()
            if user:
                logger.debug("user_found_by_email", email=email, user_id=user.id)
            return user
        except Exception as e:
            logger.error("database_error_find_by_email", email=email, error=str(e))
            raise DatabaseException(f"Failed to find user by email: {str(e)}")

    def find_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Find user by username or email"""
        try:
            user = self.db.query(User).filter(
                or_(User.username == identifier, User.email == identifier)
            ).first()
            return user
        except Exception as e:
            logger.error("database_error_find_by_identifier", identifier=identifier, error=str(e))
            raise DatabaseException(f"Failed to find user: {str(e)}")

    def create(self, user: User) -> User:
        """
        Create a new user

        Args:
            user: User object to create

        Returns:
            Created user with ID populated

        Raises:
            DatabaseException: If database error occurs
        """
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            logger.info(
                "user_created",
                user_id=user.id,
                username=user.username,
                email=user.email
            )

            return user
        except Exception as e:
            self.db.rollback()
            logger.error(
                "database_error_create_user",
                username=user.username,
                error=str(e),
                exc_info=True
            )
            raise DatabaseException(f"Failed to create user: {str(e)}")

    def update(self, user: User) -> User:
        """
        Update existing user

        Args:
            user: User object with updates

        Returns:
            Updated user

        Raises:
            UserNotFoundError: If user doesn't exist
            DatabaseException: If database error occurs
        """
        try:
            existing = self.find_by_id(user.id)
            if not existing:
                raise UserNotFoundError(str(user.id))

            self.db.commit()
            self.db.refresh(user)

            logger.info("user_updated", user_id=user.id, username=user.username)

            return user
        except UserNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("database_error_update_user", user_id=user.id, error=str(e))
            raise DatabaseException(f"Failed to update user: {str(e)}")

    def delete(self, user_id: int) -> bool:
        """
        Delete user

        Args:
            user_id: ID of user to delete

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseException: If database error occurs
        """
        try:
            user = self.find_by_id(user_id)
            if not user:
                return False

            self.db.delete(user)
            self.db.commit()

            logger.info("user_deleted", user_id=user_id)

            return True
        except Exception as e:
            self.db.rollback()
            logger.error("database_error_delete_user", user_id=user_id, error=str(e))
            raise DatabaseException(f"Failed to delete user: {str(e)}")

    def exists(self, username: str = None, email: str = None) -> bool:
        """
        Check if user exists with given username or email

        Args:
            username: Username to check
            email: Email to check

        Returns:
            True if user exists

        Raises:
            DatabaseException: If database error occurs
        """
        try:
            query = self.db.query(User)

            if username:
                query = query.filter(User.username == username)
            if email:
                query = query.filter(User.email == email)

            return query.first() is not None
        except Exception as e:
            logger.error("database_error_check_exists", username=username, email=email, error=str(e))
            raise DatabaseException(f"Failed to check user existence: {str(e)}")
