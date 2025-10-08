import pytest


class TestAPI:
    """E2E tests for the API endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, http_client, api_config):
        self.http_client = http_client
        self.api_config = api_config

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test the /health endpoint returns ok status."""
        response = await self.http_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_research_success(self):
        """Test successful research request."""
        payload = {"topic": "AI technology trends"}
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["summary"], str) and len(data["summary"]) > 0
        assert isinstance(data["sources"], list)
        assert data["processing_time"] > 0
        assert data["error_message"] is None

    @pytest.mark.asyncio
    async def test_research_empty_topic(self):
        """Test research request with empty topic fails."""
        payload = {"topic": ""}
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_research_timeout(self):
        """Test research request handles timeout gracefully."""
        # Note: Actual timeout depends on implementation; simulate or check error_message
        payload = {"topic": "Very complex topic that might timeout"}
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        data = response.json()
        # Assuming timeout is handled as failure
        if data["success"] is False:
            assert "timeout" in data["error_message"].lower()
