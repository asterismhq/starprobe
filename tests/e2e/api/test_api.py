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
        """Test research request completes with proper response structure."""
        payload = {"topic": "AI technology trends"}
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 200
        data = response.json()

        # Verify response structure exists
        assert "success" in data
        assert "summary" in data
        assert "sources" in data
        assert "processing_time" in data
        assert "error_message" in data
        assert data["processing_time"] > 0

        # Research should succeed
        assert data["success"] is True
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
    async def test_research_missing_topic(self):
        """Test research request with missing topic field fails."""
        payload = {}  # Missing topic field
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_research_null_topic(self):
        """Test research request with null topic fails."""
        payload = {"topic": None}
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_research_invalid_topic_type(self):
        """Test research request with non-string topic fails."""
        payload = {"topic": 123}  # Number instead of string
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_research_response_structure_types(self):
        """Test research response has correct types."""
        payload = {"topic": "Test topic"}
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 200
        data = response.json()

        # Type checks for response fields
        assert isinstance(data["success"], bool)
        assert isinstance(data["summary"], (str, type(None)))
        assert isinstance(data["sources"], list)
        assert all(isinstance(source, str) for source in data["sources"])
        assert isinstance(data["error_message"], (str, type(None)))
        assert isinstance(data["processing_time"], (int, float))
        assert data["processing_time"] >= 0

    @pytest.mark.asyncio
    async def test_health_response_structure(self):
        """Test health response has correct structure and types."""
        response = await self.http_client.get("/health")
        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert isinstance(data["status"], str)
        assert data["status"] == "ok"
