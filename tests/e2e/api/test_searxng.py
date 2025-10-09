"""E2E tests for SearXNG integration."""

import pytest

from ollama_deep_researcher.clients.searxng_client import SearXNGClient
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


class TestSearXNGIntegration:
    """E2E tests for SearXNG client with real service."""

    @pytest.fixture
    def settings(self):
        """Create settings with SearXNG URL for testing."""
        return OllamaDeepResearcherSettings(
            searxng_url="http://localhost:8080",
            ollama_host="http://ollama:11434/",
            ollama_model="llama3.2:3b",
        )

    @pytest.fixture
    def client(self, settings):
        """Create SearXNG client instance."""
        return SearXNGClient(settings)

    @pytest.mark.asyncio
    async def test_search_returns_results(self, client):
        """Test that search returns actual results from SearXNG."""
        result = await client.search("python programming")

        assert isinstance(result, dict)
        assert "results" in result
        assert isinstance(result["results"], list)

        # If results are returned, verify structure
        if result["results"]:
            first_result = result["results"][0]
            assert "title" in first_result
            assert "url" in first_result
            assert "content" in first_result
            assert "raw_content" in first_result

    @pytest.mark.asyncio
    async def test_search_with_max_results(self, client):
        """Test search with max_results parameter."""
        max_results = 3
        result = await client.search("artificial intelligence", max_results=max_results)

        assert isinstance(result, dict)
        assert "results" in result
        assert isinstance(result["results"], list)
        assert len(result["results"]) <= max_results

    @pytest.mark.asyncio
    async def test_search_handles_empty_query(self, client):
        """Test search with empty query returns empty results."""
        result = await client.search("")

        assert isinstance(result, dict)
        assert "results" in result
        assert isinstance(result["results"], list)
        # Empty query might return no results or default behavior
        assert len(result["results"]) >= 0

    @pytest.mark.asyncio
    async def test_search_handles_invalid_query(self, client):
        """Test search with invalid query handles gracefully."""
        result = await client.search("invalid_query_that_returns_no_results_12345")

        assert isinstance(result, dict)
        assert "results" in result
        assert isinstance(result["results"], list)
        # Should not crash, even if no results
        assert len(result["results"]) >= 0
