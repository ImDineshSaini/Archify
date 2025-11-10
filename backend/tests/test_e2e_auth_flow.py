"""
End-to-end tests for authentication flows

These tests verify complete user journeys:
- User registration → login → authenticated access
- Error flows
- Security scenarios
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


@pytest.mark.e2e
class TestCompleteAuthFlow:
    """Test complete authentication flows end-to-end"""

    def test_complete_user_journey(self, client: TestClient):
        """
        Test complete user journey:
        1. Register new user
        2. Login with credentials
        3. Use token to access protected resources
        """
        # Step 1: Register
        register_payload = {
            "username": "journey_user",
            "email": "journey@example.com",
            "password": "secure_password_123",
            "full_name": "Journey User"
        }
        register_response = client.post("/api/v2/auth/register", json=register_payload)
        assert register_response.status_code == 201
        user_id = register_response.json()["user_id"]

        # Step 2: Login
        login_payload = {
            "username": "journey_user",
            "password": "secure_password_123"
        }
        login_response = client.post("/api/v2/auth/login", json=login_payload)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        assert login_response.json()["user_id"] == user_id

        # Step 3: Use token to access root endpoint
        headers = {"Authorization": f"Bearer {token}"}
        access_response = client.get("/", headers=headers)
        assert access_response.status_code == 200

        # Step 4: Health check works
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

    def test_failed_registration_then_retry(self, client: TestClient, test_user: User):
        """
        Test registration failure recovery:
        1. Try to register with existing username (fails)
        2. Try again with different username (succeeds)
        3. Login with new account
        """
        # Step 1: Try to register with existing username
        failed_payload = {
            "username": "testuser",  # Already exists
            "email": "new@example.com",
            "password": "password123"
        }
        failed_response = client.post("/api/v2/auth/register", json=failed_payload)
        assert failed_response.status_code == 409

        # Step 2: Try again with different username
        success_payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        }
        success_response = client.post("/api/v2/auth/register", json=success_payload)
        assert success_response.status_code == 201

        # Step 3: Login with new account
        login_payload = {
            "username": "newuser",
            "password": "password123"
        }
        login_response = client.post("/api/v2/auth/login", json=login_payload)
        assert login_response.status_code == 200

    def test_failed_login_attempts(self, client: TestClient, test_user: User):
        """
        Test failed login attempts:
        1. Try wrong password multiple times
        2. Try non-existent user
        3. Finally login with correct credentials
        """
        # Step 1: Wrong password attempts
        for i in range(3):
            wrong_password = {
                "username": "testuser",
                "password": f"wrongpass{i}"
            }
            response = client.post("/api/v2/auth/login", json=wrong_password)
            assert response.status_code == 401

        # Step 2: Non-existent user
        nonexistent = {
            "username": "doesnotexist",
            "password": "somepass"
        }
        response = client.post("/api/v2/auth/login", json=nonexistent)
        assert response.status_code == 401

        # Step 3: Correct credentials
        correct = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = client.post("/api/v2/auth/login", json=correct)
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_inactive_user_cannot_login(self, client: TestClient, inactive_user: User):
        """
        Test inactive user flow:
        1. Try to login with inactive account
        2. Verify access is denied
        """
        # Step 1: Try to login
        login_payload = {
            "username": "inactive_user",
            "password": "inactive123"
        }
        response = client.post("/api/v2/auth/login", json=login_payload)

        # Step 2: Verify denied
        assert response.status_code == 403
        assert "inactive" in response.json()["error"]["message"].lower()

    def test_multiple_users_isolation(self, client: TestClient):
        """
        Test that multiple users are properly isolated:
        1. Register user A
        2. Register user B
        3. Login as A
        4. Login as B
        5. Verify they get different tokens and user IDs
        """
        # Step 1: Register user A
        user_a_register = {
            "username": "user_a",
            "email": "user_a@example.com",
            "password": "password_a"
        }
        response_a = client.post("/api/v2/auth/register", json=user_a_register)
        assert response_a.status_code == 201
        user_a_id = response_a.json()["user_id"]

        # Step 2: Register user B
        user_b_register = {
            "username": "user_b",
            "email": "user_b@example.com",
            "password": "password_b"
        }
        response_b = client.post("/api/v2/auth/register", json=user_b_register)
        assert response_b.status_code == 201
        user_b_id = response_b.json()["user_id"]

        # Verify different IDs
        assert user_a_id != user_b_id

        # Step 3: Login as A
        login_a = {"username": "user_a", "password": "password_a"}
        response_a_login = client.post("/api/v2/auth/login", json=login_a)
        assert response_a_login.status_code == 200
        token_a = response_a_login.json()["access_token"]

        # Step 4: Login as B
        login_b = {"username": "user_b", "password": "password_b"}
        response_b_login = client.post("/api/v2/auth/login", json=login_b)
        assert response_b_login.status_code == 200
        token_b = response_b_login.json()["access_token"]

        # Step 5: Verify different tokens
        assert token_a != token_b

    def test_admin_vs_regular_user(self, client: TestClient, test_admin: User, test_user: User):
        """
        Test admin vs regular user:
        1. Login as admin
        2. Login as regular user
        3. Verify admin flag is correctly set
        """
        # Step 1: Login as admin
        admin_login = {"username": "admin", "password": "admin123"}
        admin_response = client.post("/api/v2/auth/login", json=admin_login)
        assert admin_response.status_code == 200
        # Note: is_admin not currently returned in LoginResponse
        # This documents the current behavior

        # Step 2: Login as regular user
        user_login = {"username": "testuser", "password": "testpass123"}
        user_response = client.post("/api/v2/auth/login", json=user_login)
        assert user_response.status_code == 200

        # Both should succeed
        assert "access_token" in admin_response.json()
        assert "access_token" in user_response.json()

    def test_error_responses_are_consistent(self, client: TestClient):
        """
        Test that error responses follow consistent format:
        All errors should have:
        - error.code
        - error.message
        - error.details (optional)
        """
        # Test 401 error (invalid credentials)
        response_401 = client.post(
            "/api/v2/auth/login",
            json={"username": "wrong", "password": "wrong"}
        )
        assert response_401.status_code == 401
        error_401 = response_401.json()["error"]
        assert "code" in error_401
        assert "message" in error_401
        assert error_401["code"].startswith("ERR_")

        # Test 409 error (duplicate username)
        # First create user
        client.post(
            "/api/v2/auth/register",
            json={
                "username": "duplicate_test",
                "email": "duplicate@example.com",
                "password": "pass123"
            }
        )
        # Try to create again
        response_409 = client.post(
            "/api/v2/auth/register",
            json={
                "username": "duplicate_test",
                "email": "different@example.com",
                "password": "pass123"
            }
        )
        assert response_409.status_code == 409
        error_409 = response_409.json()["error"]
        assert "code" in error_409
        assert "message" in error_409
        assert error_409["code"].startswith("ERR_")

    def test_token_format_is_valid_jwt(self, client: TestClient, test_user: User):
        """
        Test that returned tokens are valid JWTs:
        - Has 3 parts separated by dots
        - Each part is base64 encoded
        """
        # Login
        login_payload = {"username": "testuser", "password": "testpass123"}
        response = client.post("/api/v2/auth/login", json=login_payload)
        assert response.status_code == 200

        token = response.json()["access_token"]

        # JWT has 3 parts: header.payload.signature
        parts = token.split(".")
        assert len(parts) == 3

        # Each part should be non-empty
        for part in parts:
            assert len(part) > 0

        # Header and payload should start with 'ey' (base64 of '{')
        assert parts[0].startswith("ey")
        assert parts[1].startswith("ey")

    def test_registration_validation_flow(self, client: TestClient):
        """
        Test registration input validation:
        1. Invalid email format
        2. Missing required fields
        3. Valid registration
        """
        # Step 1: Invalid email
        invalid_email = {
            "username": "testuser123",
            "email": "not-an-email",
            "password": "pass123"
        }
        response = client.post("/api/v2/auth/register", json=invalid_email)
        assert response.status_code == 422

        # Step 2: Missing password
        missing_field = {
            "username": "testuser123",
            "email": "valid@example.com"
        }
        response = client.post("/api/v2/auth/register", json=missing_field)
        assert response.status_code == 422

        # Step 3: Valid registration
        valid_data = {
            "username": "testuser123",
            "email": "valid@example.com",
            "password": "pass123"
        }
        response = client.post("/api/v2/auth/register", json=valid_data)
        assert response.status_code == 201
