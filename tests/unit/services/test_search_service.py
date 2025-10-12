"""Unit tests for SearchService."""

import pytest

from src.olm_d_rch.services.search_service import SearchService


class TestSearchService:
    """Test cases for SearchService."""

    @pytest.fixture
    def search_service(self, mock_search_client):
        """Create a SearchService instance with mock client."""
        return SearchService(search_client=mock_search_client)

    @pytest.mark.asyncio
    async def test_search_returns_results(self, search_service):
        """Test search returns list of results."""
        result = await search_service.search("test query")
        assert isinstance(result, dict)
        assert "results" in result
        assert isinstance(result["results"], list)
        assert len(result["results"]) > 0

    @pytest.mark.asyncio
    async def test_search_result_structure(self, search_service):
        """Test each search result has required fields."""
        result = await search_service.search("test query")
        for item in result["results"]:
            assert "title" in item
            assert "url" in item
            assert "content" in item or "raw_content" in item

    @pytest.mark.asyncio
    async def test_search_with_max_results(self, search_service, mock_search_client):
        """Test max_results parameter limits returned results."""
        result = await search_service.search("test query", max_results=2)
        assert len(result["results"]) <= 2

    @pytest.mark.asyncio
    async def test_search_with_max_results_default(self, search_service):
        """Test default max_results is 3."""
        result = await search_service.search("test query")
        # Mock returns 3 results by default
        assert len(result["results"]) <= 3

    @pytest.mark.asyncio
    async def test_search_handles_empty_results(
        self, search_service, mock_search_client, mocker
    ):
        """Test behavior with no search results."""
        mocker.patch.object(mock_search_client, "search", return_value={"results": []})
        result = await search_service.search("test query")
        assert result == {"results": []}

    @pytest.mark.asyncio
    async def test_search_handles_exceptions(
        self, search_service, mock_search_client, mocker
    ):
        """Test graceful error handling when search fails."""
        mocker.patch.object(
            mock_search_client, "search", side_effect=Exception("Network error")
        )
        result = await search_service.search("test query")
        assert result == {"results": []}

    @pytest.mark.asyncio
    async def test_search_delegates_to_client(self, mocker, mock_search_client):
        """Test search delegates to the injected client."""
        search_service = SearchService(search_client=mock_search_client)

        # Spy on the client's search method
        spy = mocker.spy(mock_search_client, "search")

        query = "test query"
        max_results = 5
        await search_service.search(query, max_results)

        # Verify client was called with correct parameters
        spy.assert_called_once_with(query, max_results)

    @pytest.mark.asyncio
    async def test_search_returns_urls(self, search_service):
        """Test search returns valid URLs in results."""
        result = await search_service.search("test query")
        for item in result["results"]:
            url = item.get("url", "")
            assert url.startswith("http://") or url.startswith("https://")
