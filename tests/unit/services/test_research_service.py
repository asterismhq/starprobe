"""Unit tests for ResearchService."""

import pytest

from src.olm_d_rch.container import DependencyContainer


class TestResearchService:
    """Test cases for ResearchService."""

    @pytest.fixture
    async def research_service(self):
        """Create a ResearchService instance with mocked dependencies."""
        container = DependencyContainer()
        return container.research_service

    @pytest.mark.asyncio
    async def test_search_and_scrape_success(self, mocker, research_service):
        """Test successful search and scrape workflow."""
        # Set mock return value
        mocker.patch.object(
            research_service.search_client,
            "search",
            return_value={
                "results": [
                    {
                        "url": "https://example.com/1",
                        "title": "Result 1",
                        "content": "Short snippet 1",
                    },
                    {
                        "url": "https://example.com/2",
                        "title": "Result 2",
                        "content": "Short snippet 2",
                    },
                ]
            },
        )
        mocker.patch.object(
            research_service.scraper,
            "scrape",
            return_value="Mocked scraped content",
        )

        search_str, sources, errors = await research_service.search_and_scrape(
            "test query", loop_count=1
        )

        # Should return tuple of strings
        assert isinstance(search_str, str)
        assert isinstance(sources, str)
        assert errors == []

        # Should contain URLs
        assert (
            "https://example.com/1" in search_str or "https://example.com/1" in sources
        )
        assert (
            "https://example.com/2" in search_str or "https://example.com/2" in sources
        )

    @pytest.mark.asyncio
    async def test_search_and_scrape_with_scraping(self, mocker, research_service):
        """Test that scraping is called for each URL."""
        spy = mocker.spy(research_service.scraper, "scrape")

        _, _, errors = await research_service.search_and_scrape(
            "test query", loop_count=1
        )

        # Verify scraping was called
        spy.assert_called()
        assert errors == []

    @pytest.mark.asyncio
    async def test_search_and_scrape_with_failed_scraping(
        self, mocker, research_service
    ):
        """Test behavior when some URLs fail to scrape."""
        # Set scraper to fail on second URL
        mocker.patch.object(
            research_service.scraper,
            "scrape",
            side_effect=["Scraped content 1", Exception("Network error")],
        )

        search_str, sources, errors = await research_service.search_and_scrape(
            "test query", loop_count=1
        )

        # Should still return results despite scraping failure
        # Scraping failures are logged but not treated as errors (fallback to snippet)
        assert isinstance(search_str, str)
        assert isinstance(sources, str)
        assert errors == []

    @pytest.mark.asyncio
    async def test_search_and_scrape_empty_results(self, mocker, research_service):
        """Test behavior with no search results."""
        # Set mock to return empty results
        mocker.patch.object(
            research_service.search_client, "search", return_value={"results": []}
        )

        search_str, sources, errors = await research_service.search_and_scrape(
            "test query", loop_count=1
        )

        # Should return empty strings or defaults
        assert isinstance(search_str, str)
        assert isinstance(sources, str)
        assert errors  # fallback diagnostics should be recorded

    @pytest.mark.asyncio
    async def test_search_and_scrape_respects_max_results(
        self, mocker, research_service
    ):
        """Test that search is called with max_results=3."""
        # Spy on the search method
        spy = mocker.spy(research_service.search_client, "search")
        research_service.search_client.search.return_value = {"results": []}

        await research_service.search_and_scrape("test query", loop_count=1)

        # Verify both the primary and fallback queries were attempted with max_results=3
        call_args = spy.call_args_list
        assert call_args  # ensure at least one call
        assert call_args[0].kwargs == {"max_results": 3}
        assert call_args[0].args[0] == "test query"
        # Fallback query should also respect the max_results parameter
        for call in call_args:
            assert call.kwargs == {"max_results": 3}

    @pytest.mark.asyncio
    async def test_search_and_scrape_handles_missing_url(
        self, mocker, research_service
    ):
        """Test handling of search results without URLs."""
        mocker.patch.object(
            research_service.search_client,
            "search",
            return_value={
                "results": [
                    {"title": "Result without URL", "content": "Some content"},
                    {
                        "url": "https://example.com/1",
                        "title": "Valid result",
                        "content": "Content",
                    },
                ]
            },
        )

        # Should not raise error with missing URL
        search_str, sources, errors = await research_service.search_and_scrape(
            "test query", loop_count=1
        )

        assert isinstance(search_str, str)
        assert isinstance(sources, str)
        assert errors == []

    @pytest.mark.asyncio
    async def test_search_and_scrape_handles_search_exception(
        self, mocker, research_service
    ):
        """Test graceful error handling when search fails."""
        mocker.patch.object(
            research_service.search_client,
            "search",
            side_effect=Exception("Search API error"),
        )

        search_str, sources, errors = await research_service.search_and_scrape(
            "test query", loop_count=1
        )

        # Should return error messages instead of raising
        assert isinstance(search_str, str)
        assert isinstance(sources, str)
        assert any("Primary search failed" in err for err in errors)

    @pytest.mark.asyncio
    async def test_search_and_scrape_updates_raw_content(
        self, mocker, research_service
    ):
        """Test that raw_content is updated with scraped content."""
        search_results = {
            "results": [
                {
                    "url": "https://example.com/1",
                    "title": "Result 1",
                    "content": "Short snippet",
                }
            ]
        }

        mocker.patch.object(
            research_service.search_client, "search", return_value=search_results
        )
        mocker.patch.object(
            research_service.scraper,
            "scrape",
            return_value="Full scraped content from the page",
        )

        search_str, sources, errors = await research_service.search_and_scrape(
            "test query", loop_count=1
        )

        # Should contain the scraped content
        assert "Full scraped content" in search_str
        assert errors == []

    @pytest.mark.asyncio
    async def test_perform_search_delegates_to_client(self, mocker, research_service):
        """Test _perform_search delegates to search client."""
        mocker.patch.object(
            research_service.search_client, "search", return_value={"results": []}
        )

        result = await research_service._perform_search("test query", loop_count=1)

        # Should call search client with correct parameters
        research_service.search_client.search.assert_called_once_with(
            "test query", max_results=3
        )
        assert result == {"results": []}
