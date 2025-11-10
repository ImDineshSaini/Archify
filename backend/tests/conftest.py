"""
Test configuration and fixtures

This module provides common fixtures for all tests including:
- Test database setup
- Test client
- Test users
- Mock dependencies
"""

import os
import pytest
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from faker import Faker

# Set test environment BEFORE importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["DEBUG"] = "True"
os.environ["ENABLE_MULTI_TENANCY"] = "false"

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import settings

# Initialize Faker for generating test data
fake = Faker()


# Database Fixtures
@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create a test database using SQLite in-memory database.

    This fixture:
    - Creates a fresh database for each test
    - Automatically rolls back changes after each test
    - Uses SQLite for speed (no need for PostgreSQL)

    Scope: function (new database for each test)
    """
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with overridden database dependency.

    This fixture:
    - Provides a TestClient for making API requests
    - Overrides the get_db dependency to use test database
    - Automatically handles session cleanup
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# User Fixtures
@pytest.fixture
def test_user(test_db: Session) -> User:
    """
    Create a test user in the database.

    Returns a regular (non-admin) user with known credentials:
    - username: testuser
    - password: testpass123
    - email: test@example.com
    """
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        is_active=True,
        is_admin=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_admin(test_db: Session) -> User:
    """
    Create a test admin user in the database.

    Returns an admin user with known credentials:
    - username: admin
    - password: admin123
    - email: admin@example.com
    """
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        is_active=True,
        is_admin=True
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture
def inactive_user(test_db: Session) -> User:
    """
    Create an inactive test user.

    Returns an inactive user for testing access restrictions:
    - username: inactive_user
    - password: inactive123
    - is_active: False
    """
    user = User(
        username="inactive_user",
        email="inactive@example.com",
        hashed_password=get_password_hash("inactive123"),
        full_name="Inactive User",
        is_active=False,
        is_admin=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def multiple_users(test_db: Session) -> list[User]:
    """
    Create multiple test users for testing list operations.

    Returns a list of 5 users with random data.
    """
    users = []
    for i in range(5):
        user = User(
            username=f"user{i}_{fake.user_name()}",
            email=fake.email(),
            hashed_password=get_password_hash(f"password{i}"),
            full_name=fake.name(),
            is_active=True,
            is_admin=False
        )
        test_db.add(user)
        users.append(user)

    test_db.commit()
    for user in users:
        test_db.refresh(user)

    return users


# Authentication Fixtures
@pytest.fixture
def auth_headers(client: TestClient, test_user: User) -> dict:
    """
    Get authentication headers for test user.

    Returns headers with valid JWT token for test_user.
    Use this for authenticated requests.
    """
    response = client.post(
        "/api/v2/auth/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client: TestClient, test_admin: User) -> dict:
    """
    Get authentication headers for admin user.

    Returns headers with valid JWT token for admin user.
    Use this for admin-only requests.
    """
    response = client.post(
        "/api/v2/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Helper Fixtures
@pytest.fixture
def faker() -> Faker:
    """Provide Faker instance for generating test data"""
    return Faker()


# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """
    Mock settings for testing.

    This fixture automatically applies to all tests and ensures:
    - DEBUG mode is enabled
    - Multi-tenancy is disabled (unless test explicitly enables it)
    - Safe test values for all settings
    """
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("ENABLE_MULTI_TENANCY", "false")
    # Don't override other settings - let .env.example values be used
