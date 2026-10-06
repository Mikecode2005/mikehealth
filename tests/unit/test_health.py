"""Unit tests for health endpoints."""
import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test basic health check endpoint."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "version" in data
        assert "environment" in data
        assert "database" in data

    @pytest.mark.asyncio
    async def test_readiness_check(self, async_client: AsyncClient):
        """Test Kubernetes readiness probe."""
        response = await async_client.get("/ready")
        assert response.status_code in [200, 503]
        data = response.json()
        assert data["status"] in ["ready", "not ready"]

    @pytest.mark.asyncio
    async def test_liveness_check(self, async_client: AsyncClient):
        """Test Kubernetes liveness probe."""
        response = await async_client.get("/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint."""
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "mikehealth API"
        assert "version" in data
        assert "docs" in data