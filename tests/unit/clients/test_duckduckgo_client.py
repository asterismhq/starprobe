"""Unit tests for DuckDuckGoClient."""

import pytest

from ollama_deep_researcher.clients.duckduckgo_client import DuckDuckGoClient


class TestDuckDuckGoClient:
    """Test cases for DuckDuckGoClient."""

    @pytest.fixture
    def mock_ddgs(self, mocker):
        """Create a mock DDGS instance."""
        mock_ddgs_instance = mocker.MagicMock()

        # Mock the text() method to return sample results
        mock_ddgs_instance.text.return_value = [
            {
                "href": "https://example.com/1",
                "title": "Example Result 1",
                "body": "This is the content snippet for result 1",
            },
            {
                "href": "https://example.com/2",
                "title": "Example Result 2",
                "body": "This is the content snippet for result 2",
            },
            {
                "href": "https://example.com/3",
                "title": "Example Result 3",
                "body": "This is the content snippet for result 3",
            },
        ]

        # Mock the DDGS context manager
        mock_ddgs_instance.__enter__.return_value = mock_ddgs_instance
        mock_ddgs_instance.__exit__.return_value = None

        # Patch the DDGS class from ddgs module
        mock_ddgs_class = mocker.patch("ddgs.DDGS")
        mock_ddgs_class.return_value = mock_ddgs_instance

        return mock_ddgs_instance

    def test_search_returns_results(self, mock_ddgs):
        """Test search returns properly formatted results."""
        client = DuckDuckGoClient()
        result = client.search("test query")

        assert isinstance(result, dict)
        assert "results" in result
        assert isinstance(result["results"], list)
        assert len(result["results"]) > 0

    def test_search_result_structure(self, mock_ddgs):
        """Test each result has required fields."""
        client = DuckDuckGoClient()
        result = client.search("test query")

        for item in result["results"]:
            assert "title" in item
            assert "url" in item
            assert "content" in item
            assert "raw_content" in item

    def test_search_formats_results_correctly(self, mock_ddgs):
        """Test result structure matches expected format."""
        client = DuckDuckGoClient()
        result = client.search("test query")

        first_result = result["results"][0]
        assert first_result["title"] == "Example Result 1"
        assert first_result["url"] == "https://example.com/1"
        assert first_result["content"] == "This is the content snippet for result 1"
        assert first_result["raw_content"] == first_result["content"]

    def test_search_with_max_results(self, mock_ddgs):
        """Test max_results parameter is passed to DDGS."""
        client = DuckDuckGoClient()
        client.search("test query", max_results=2)

        # Verify text() was called with max_results=2
        mock_ddgs.text.assert_called_once_with("test query", max_results=2)

    def test_search_with_default_max_results(self, mock_ddgs):
        """Test default max_results is 3."""
        client = DuckDuckGoClient()
        client.search("test query")

        # Verify text() was called with default max_results=3
        mock_ddgs.text.assert_called_once_with("test query", max_results=3)

    def test_search_handles_incomplete_results(self, mock_ddgs):
        """Test filtering of results with missing fields."""
        # Mock results with incomplete data
        mock_ddgs.text.return_value = [
            {
                "href": "https://example.com/1",
                "title": "Complete Result",
                "body": "Complete content",
            },
            {
                "href": "https://example.com/2",
                "title": "Incomplete Result",
                # Missing 'body'
            },
            {
                "href": "https://example.com/3",
                # Missing 'title' and 'body'
            },
        ]

        client = DuckDuckGoClient()
        result = client.search("test query")

        # Should only have 1 complete result
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Complete Result"

    def test_search_handles_exceptions(self, mock_ddgs):
        """Test graceful error handling when search fails."""
        mock_ddgs.text.side_effect = Exception("Network error")

        client = DuckDuckGoClient()
        result = client.search("test query")

        # Should return empty results on error
        assert result == {"results": []}

    def test_search_empty_results(self, mock_ddgs):
        """Test handling of empty search results."""
        mock_ddgs.text.return_value = []

        client = DuckDuckGoClient()
        result = client.search("test query")

        assert result == {"results": []}

    def test_search_creates_ddgs_client(self, mocker):
        """Test that DDGS client is created on initialization."""
        mock_ddgs_class = mocker.patch("ddgs.DDGS")

        DuckDuckGoClient()

        # Verify DDGS was instantiated
        mock_ddgs_class.assert_called_once()
