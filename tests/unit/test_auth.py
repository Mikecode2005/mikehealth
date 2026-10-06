"""Unit tests for authentication."""
import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    @pytest.mark.asyncio
    async def test_register_user(self, async_client: AsyncClient):
        """Test user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "role": "doctor",
        }
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["role"] == user_data["role"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client: AsyncClient):
        """Test registration with duplicate email."""
        user_data = {
            "email": "duplicate@example.com",
            "password": "password123",
            "full_name": "Duplicate User",
            "role": "doctor",
        }
        # First registration
        await async_client.post("/api/v1/auth/register", json=user_data)
        # Second registration should fail
        response = await async_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, test_user):
        """Test successful login."""
        login_data = {
            "email": test_user.email,
            "password": "password123",
        }
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        }
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, async_client: AsyncClient, test_user):
        """Test getting current user info."""
        # Login first
        login_data = {"email": test_user.email, "password": "password123"}
        login_response = await async_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]

        # Get current user
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name