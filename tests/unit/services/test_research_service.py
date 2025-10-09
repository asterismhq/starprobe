"""Unit tests for ResearchService."""

import pytest

from ollama_deep_researcher.services.research_service import ResearchService


class TestResearchService:
    """Test cases for ResearchService."""

    @pytest.fixture
    async def research_service(self, mock_settings, mock_scraping_service, mocker):
        """Create a ResearchService instance with mocked dependencies."""
        mock_search_client = mocker.AsyncMock()
        mock_search_client.search.return_value = {
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
        }

        return ResearchService(
            settings=mock_settings,
            search_client=mock_search_client,
            scraper=mock_scraping_service,
        )

    @pytest.mark.asyncio
    async def test_search_and_scrape_success(self, research_service):
        """Test successful search and scrape workflow."""
        search_str, sources, errors, warnings = (
            await research_service.search_and_scrape("test query", loop_count=1)
        )

        # Should return tuple of strings
        assert isinstance(search_str, str)
        assert isinstance(sources, str)
        assert errors == []
        assert warnings == []

        # Should contain URLs
        assert (
            "https://example.com/1" in search_str or "https://example.com/1" in sources
        )
        assert (
            "https://example.com/2" in search_str or "https://example.com/2" in sources
        )

    @pytest.mark.asyncio
    async def test_search_and_scrape_with_scraping(
        self, mock_settings, mock_scraping_service, mocker
    ):
        """Test that scraping is called for each URL."""
        mock_search_client = mocker.AsyncMock()
        mock_search_client.search.return_value = {
            "results": [
                {
                    "url": "https://example.com/1",
                    "title": "Result 1",
                    "content": "Snippet",
                }
            ]
        }

        research_service = ResearchService(
            settings=mock_settings,
            search_client=mock_search_client,
            scraper=mock_scraping_service,
        )

        spy = mocker.spy(mock_scraping_service, "scrape")

        _, _, errors, warnings = await research_service.search_and_scrape(
            "test query", loop_count=1
        )

        # Verify scraping was called
        spy.assert_called()
        assert errors == []
        assert warnings == []

    @pytest.mark.asyncio
    async def test_search_and_scrape_with_failed_scraping(self, mock_settings, mocker):
        """Test behavior when some URLs fail to scrape."""
        mock_search_client = mocker.AsyncMock()
        mock_search_client.search.return_value = {
            "results": [
                {
                    "url": "https://example.com/1",
                    "title": "Result 1",
                    "content": "Snippet 1",
                },
                {
                    "url": "https://example.com/2",
                    "title": "Result 2",
                    "content": "Snippet 2",
                },
            ]
        }

        # Mock scraper that fails on second URL
        mock_scraper = mocker.Mock()
        mock_scraper.scrape.side_effect = [
            "Scraped content 1",
            Exception("Network error"),
        ]

        research_service = ResearchService(
            settings=mock_settings,
            search_client=mock_search_client,
            scraper=mock_scraper,
        )

        search_str, sources, errors, warnings = (
            await research_service.search_and_scrape("test query", loop_count=1)
        )

        # Should still return results despite scraping failure
        assert isinstance(search_str, str)
        assert isinstance(sources, str)
        assert errors == []
        assert any("Scraping failed" in warn for warn in warnings)

    @pytest.mark.asyncio
    async def test_search_and_scrape_empty_results(
        self, mock_settings, mock_scraping_service, mocker
    ):
        """Test behavior with no search results."""
        mock_search_client = mocker.AsyncMock()
        mock_search_client.search.return_value = {"results": []}

        research_service = ResearchService(
            settings=mock_settings,
            search_client=mock_search_client,
            scraper=mock_scraping_service,
        )

        search_str, sources, errors, warnings = (
            await research_service.search_and_scrape("test query", loop_count=1)
        )

        # Should return empty strings or defaults
        assert isinstance(search_str, str)
        assert isinstance(sources, str)
        assert errors  # fallback diagnostics should be recorded
        assert isinstance(warnings, list)

    @pytest.mark.asyncio
    async def test_search_and_scrape_respects_max_results(
        self, mock_settings, mock_scraping_service, mocker
    ):
        """Test that search is called with max_results=3."""
        mock_search_client = mocker.AsyncMock()
        mock_search_client.search.return_value = {"results": []}

        research_service = ResearchService(
            settings=mock_settings,
            search_client=mock_search_client,
            scraper=mock_scraping_service,
        )

        await research_service.search_and_scrape("test query", loop_count=1)

        # Verify both the primary and fallback queries were attempted with max_results=3
        call_args = mock_search_client.search.call_args_list
        assert call_args  # ensure at least one call
        assert call_args[0].kwargs == {"max_results": 3}
        assert call_args[0].args[0] == "test query"
        # Fallback query should also respect the max_results parameter
        for call in call_args:
            assert call.kwargs == {"max_results": 3}

    @pytest.mark.asyncio
    async def test_search_and_scrape_handles_missing_url(
        self, mock_settings, mock_scraping_service, mocker
    ):
        """Test handling of search results without URLs."""
        mock_search_client = mocker.AsyncMock()
        mock_search_client.search.return_value = {
            "results": [
                {"title": "Result without URL", "content": "Some content"},
                {
                    "url": "https://example.com/1",
                    "title": "Valid result",
                    "content": "Content",
                },
            ]
        }

        research_service = ResearchService(
            settings=mock_settings,
            search_client=mock_search_client,
            scraper=mock_scraping_service,
        )

        # Should not raise error with missing URL
        search_str, sources, errors, warnings = (
            await research_service.search_and_scrape("test query", loop_count=1)
        )

        assert isinstance(search_str, str)
        assert isinstance(sources, str)
        assert errors == []
        assert warnings == []

    @pytest.mark.asyncio
    async def test_search_and_scrape_handles_search_exception(
        self, mock_settings, mock_scraping_service, mocker
    ):
        """Test graceful error handling when search fails."""
        mock_search_client = mocker.AsyncMock()
        mock_search_client.search.side_effect = Exception("Search API error")

        research_service = ResearchService(
            settings=mock_settings,
            search_client=mock_search_client,
            scraper=mock_scraping_service,
        )

        search_str, sources, errors, warnings = (
            await research_service.search_and_scrape("test query", loop_count=1)
        )

        # Should return error messages instead of raising
        assert isinstance(search_str, str)
        assert isinstance(sources, str)
        assert any("Primary search failed" in err for err in errors)
        assert isinstance(warnings, list)

    @pytest.mark.asyncio
    async def test_search_and_scrape_updates_raw_content(
        self, mock_settings, mock_scraping_service, mocker
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

        mock_search_client = mocker.AsyncMock()
        mock_search_client.search.return_value = search_results

        # Mock scraper to return specific content
        mock_scraper = mocker.Mock()
        mock_scraper.scrape.return_value = "Full scraped content from the page"

        research_service = ResearchService(
            settings=mock_settings,
            search_client=mock_search_client,
            scraper=mock_scraper,
        )

        search_str, sources, errors, warnings = (
            await research_service.search_and_scrape("test query", loop_count=1)
        )

        # Should contain the scraped content
        assert "Full scraped content" in search_str
        assert errors == []
        assert warnings == []

    @pytest.mark.asyncio
    async def test_perform_search_delegates_to_client(
        self, mock_settings, mock_scraping_service, mocker
    ):
        """Test _perform_search delegates to search client."""
        mock_search_client = mocker.AsyncMock()
        mock_search_client.search.return_value = {"results": []}

        research_service = ResearchService(
            settings=mock_settings,
            search_client=mock_search_client,
            scraper=mock_scraping_service,
        )

        result = await research_service._perform_search("test query", loop_count=1)

        # Should call search client with correct parameters
        mock_search_client.search.assert_called_once_with("test query", max_results=3)
        assert result == {"results": []}
