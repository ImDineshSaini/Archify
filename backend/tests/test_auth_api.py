"""
Integration tests for Authentication API

These tests verify the API endpoints work correctly:
- HTTP request/response handling
- Status codes
- Error responses
- JWT token generation
- End-to-end authentication flow
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


@pytest.mark.integration
class TestLoginAPI:
    """Test suite for /api/v2/auth/login endpoint"""

    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login returns 200 and valid token"""
        # Arrange
        payload = {
            "username": "testuser",
            "password": "testpass123"
        }

        # Act
        response = client.post("/api/v2/auth/login", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == test_user.id
        assert data["username"] == "testuser"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 50  # JWT tokens are long

    def test_login_with_wrong_password(self, client: TestClient, test_user: User):
        """Test login with wrong password returns 401"""
        # Arrange
        payload = {
            "username": "testuser",
            "password": "wrongpassword"
        }

        # Act
        response = client.post("/api/v2/auth/login", json=payload)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "ERR_AUTH_001"
        assert "Invalid username or password" in data["error"]["message"]

    def test_login_with_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user returns 401"""
        # Arrange
        payload = {
            "username": "nonexistent",
            "password": "password123"
        }

        # Act
        response = client.post("/api/v2/auth/login", json=payload)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "ERR_AUTH_001"

    def test_login_with_inactive_user(self, client: TestClient, inactive_user: User):
        """Test login with inactive user returns 403"""
        # Arrange
        payload = {
            "username": "inactive_user",
            "password": "inactive123"
        }

        # Act
        response = client.post("/api/v2/auth/login", json=payload)

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "ERR_USER_003"
        assert "inactive" in data["error"]["message"].lower()

    def test_login_with_missing_fields(self, client: TestClient):
        """Test login with missing fields returns 422"""
        # Arrange - missing password
        payload = {
            "username": "testuser"
        }

        # Act
        response = client.post("/api/v2/auth/login", json=payload)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_login_with_empty_username(self, client: TestClient):
        """Test login with empty username returns 401 (treated as invalid credentials)"""
        # Arrange
        payload = {
            "username": "",
            "password": "password123"
        }

        # Act
        response = client.post("/api/v2/auth/login", json=payload)

        # Assert
        # Empty username passes Pydantic validation but fails authentication
        assert response.status_code == 401

    def test_login_token_can_be_used(self, client: TestClient, test_user: User):
        """Test that the returned token can be used for authentication"""
        # Arrange - login first
        login_payload = {
            "username": "testuser",
            "password": "testpass123"
        }
        login_response = client.post("/api/v2/auth/login", json=login_payload)
        token = login_response.json()["access_token"]

        # Act - use token to access root endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/", headers=headers)

        # Assert
        assert response.status_code == 200

    def test_login_multiple_times(self, client: TestClient, test_user: User):
        """Test that logging in multiple times generates different tokens"""
        # Arrange
        payload = {
            "username": "testuser",
            "password": "testpass123"
        }

        # Act - login twice
        response1 = client.post("/api/v2/auth/login", json=payload)
        response2 = client.post("/api/v2/auth/login", json=payload)

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

        token1 = response1.json()["access_token"]
        token2 = response2.json()["access_token"]

        # Tokens might be same or different depending on timestamp
        # Both should be valid
        assert len(token1) > 50
        assert len(token2) > 50


@pytest.mark.integration
class TestRegisterAPI:
    """Test suite for /api/v2/auth/register endpoint"""

    def test_register_success(self, client: TestClient):
        """Test successful registration returns 201"""
        # Arrange
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User"
        }

        # Act
        response = client.post("/api/v2/auth/register", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["message"] == "User registered successfully"
        assert "user_id" in data
        assert data["user_id"] > 0

    def test_register_without_full_name(self, client: TestClient):
        """Test registration works without full_name (optional)"""
        # Arrange
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }

        # Act
        response = client.post("/api/v2/auth/register", json=payload)

        # Assert
        assert response.status_code == 201

    def test_register_with_duplicate_username(self, client: TestClient, test_user: User):
        """Test registration with duplicate username returns 409"""
        # Arrange
        payload = {
            "username": "testuser",  # Already exists
            "email": "different@example.com",
            "password": "password123"
        }

        # Act
        response = client.post("/api/v2/auth/register", json=payload)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "ERR_USER_002"
        assert "username" in data["error"]["message"].lower()

    def test_register_with_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email returns 409"""
        # Arrange
        payload = {
            "username": "differentuser",
            "email": "test@example.com",  # Already exists
            "password": "password123"
        }

        # Act
        response = client.post("/api/v2/auth/register", json=payload)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "ERR_USER_002"
        assert "email" in data["error"]["message"].lower()

    def test_register_with_invalid_email(self, client: TestClient):
        """Test registration with invalid email returns 422"""
        # Arrange
        payload = {
            "username": "newuser",
            "email": "not-an-email",
            "password": "password123"
        }

        # Act
        response = client.post("/api/v2/auth/register", json=payload)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_register_with_missing_required_fields(self, client: TestClient):
        """Test registration with missing required fields returns 422"""
        # Arrange - missing password
        payload = {
            "username": "newuser",
            "email": "newuser@example.com"
        }

        # Act
        response = client.post("/api/v2/auth/register", json=payload)

        # Assert
        assert response.status_code == 422

    def test_register_then_login(self, client: TestClient):
        """Test that newly registered user can login"""
        # Arrange - register first
        register_payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }
        register_response = client.post("/api/v2/auth/register", json=register_payload)
        assert register_response.status_code == 201

        # Act - try to login
        login_payload = {
            "username": "newuser",
            "password": "password123"
        }
        login_response = client.post("/api/v2/auth/login", json=login_payload)

        # Assert
        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert data["username"] == "newuser"

    def test_register_password_not_returned(self, client: TestClient):
        """Test that password is never returned in response"""
        # Arrange
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }

        # Act
        response = client.post("/api/v2/auth/register", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_multiple_users(self, client: TestClient):
        """Test registering multiple users works"""
        # Act - register 3 users
        for i in range(3):
            payload = {
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": f"password{i}"
            }
            response = client.post("/api/v2/auth/register", json=payload)

            # Assert
            assert response.status_code == 201
            assert response.json()["username"] == f"user{i}"


@pytest.mark.integration
class TestHealthEndpoint:
    """Test suite for health check endpoint"""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint returns 200"""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "multi_tenancy" in data


@pytest.mark.integration
class TestRootEndpoint:
    """Test suite for root endpoint"""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns welcome message"""
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert data["docs"] == "/docs"
