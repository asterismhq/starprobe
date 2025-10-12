import pytest


class TestIntgAPI:
    """Integration tests for the API endpoints with mocked dependencies."""

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
        """Test research request completes with proper response structure and types."""
        payload = {"query": "AI technology trends"}
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 200
        data = response.json()

        # Verify response structure exists
        assert "success" in data
        assert "article" in data
        assert "metadata" in data
        assert "processing_time" in data
        assert "error_message" in data
        assert "diagnostics" in data
        assert data["processing_time"] > 0

        # Research should succeed - print full response on failure
        assert data["success"] is True, (
            f"Research failed. Full response:\n"
            f"  success: {data['success']}\n"
            f"  error_message: {data['error_message']}\n"
            f"  diagnostics: {data['diagnostics']}\n"
            f"  article: {data['article'][:100] if data['article'] else None}...\n"
            f"  metadata: {data['metadata']}\n"
            f"  processing_time: {data['processing_time']}"
        )
        assert (
            data["error_message"] is None
        ), f"Expected no error but got: {data['error_message']}"
        # Diagnostics may contain warnings (non-critical) even on success
        # Only check that there are no critical errors by verifying success=True

        # Type checks for response fields
        assert isinstance(data["success"], bool)
        assert isinstance(data["article"], (str, type(None)))
        assert isinstance(data["metadata"], (dict, type(None)))
        if data["success"]:
            assert data["metadata"] is not None
            assert "source_count" in data["metadata"]
            assert "sources" in data["metadata"]
            assert isinstance(data["metadata"]["sources"], list)
        assert isinstance(data["error_message"], (str, type(None)))
        assert isinstance(data["diagnostics"], list)
        assert all(isinstance(msg, str) for msg in data["diagnostics"])
        assert isinstance(data["processing_time"], (int, float))
        assert data["processing_time"] >= 0

    @pytest.mark.asyncio
    async def test_research_success_with_mlx_backend(self):
        """Test research request using the MLX backend succeeds."""
        payload = {"query": "Climate change impacts", "backend": "mlx"}
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["error_message"] is None
        assert isinstance(data["article"], (str, type(None)))
        assert isinstance(data["metadata"], (dict, type(None)))
        assert isinstance(data["diagnostics"], list)

    @pytest.mark.asyncio
    async def test_research_empty_query(self):
        """Test research request with empty query fails."""
        payload = {"query": ""}
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_research_missing_query(self):
        """Test research request with missing query field fails."""
        payload = {}  # Missing query field
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_research_null_query(self):
        """Test research request with null query fails."""
        payload = {"query": None}
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_research_invalid_query_type(self):
        """Test research request with non-string query fails."""
        payload = {"query": 123}  # Number instead of string
        response = await self.http_client.post(
            self.api_config["research_url"], json=payload
        )
        assert response.status_code == 422  # Pydantic validation error

    async def test_health_response_structure(self):
        """Test health response has correct structure and types."""
        response = await self.http_client.get("/health")
        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert isinstance(data["status"], str)
        assert data["status"] == "ok"
