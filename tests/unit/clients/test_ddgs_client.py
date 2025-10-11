"""Unit tests for DdgsClient."""

import pytest
from ddgs.exceptions import DDGSException


def test_ddgs_client_uses_unit_test_settings():
    """
    Ensure the DDGS client is initialized with automatically applied unit test settings.
    """
    from olm_d_rch.config.ddgs_settings import DDGSSettings

    # Recreate settings instance to pick up monkeypatched env vars
    settings = DDGSSettings()
    # Verify that the default values are used since unit tests don't override them
    assert settings.ddgs_safesearch == "moderate"
    assert settings.ddgs_max_results == 10


class TestDdgsClient:
    """Test cases for DdgsClient."""

    @pytest.fixture
    def client(self, mocker):
        """Create a DdgsClient instance with mocked DDGS."""
        from olm_d_rch.clients.ddgs_client import DdgsClient
        from olm_d_rch.config.ddgs_settings import DDGSSettings

        mock_ddgs_instance = mocker.Mock()
        mocker.patch(
            "olm_d_rch.clients.ddgs_client.DDGS",
            return_value=mock_ddgs_instance,
        )

        settings = DDGSSettings()
        client = DdgsClient(settings)
        client._mock_ddgs = mock_ddgs_instance  # Attach mock for test access
        return client

    @pytest.mark.asyncio
    async def test_search_returns_results(self, client):
        client._mock_ddgs.text.return_value = [
            {
                "title": "Example Result 1",
                "href": "https://example.com/1",
                "body": "Snippet 1",
            }
        ]

        result = await client.search("python")

        assert result == {
            "results": [
                {
                    "title": "Example Result 1",
                    "url": "https://example.com/1",
                    "content": "Snippet 1",
                    "raw_content": "",  # Left empty so ResearchService can scrape
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_search_trims_to_max_results(self, client):
        all_results = [
            {
                "title": f"Result {idx}",
                "href": f"https://example.com/{idx}",
                "body": f"Snippet {idx}",
            }
            for idx in range(5)
        ]
        client._mock_ddgs.text.side_effect = (
            lambda query, region=None, safesearch=None, max_results=3: all_results[
                :max_results
            ]
        )

        result = await client.search("python", max_results=2)

        assert len(result["results"]) == 2
        client._mock_ddgs.text.assert_called_once_with(
            "python",
            region=client.settings.ddgs_region,
            safesearch=client.settings.ddgs_safesearch,
            max_results=2,
        )

    @pytest.mark.asyncio
    async def test_search_skips_incomplete_results(self, client):
        client._mock_ddgs.text.return_value = [
            {"title": "Missing URL"},
            {"href": "https://example.com/1"},
            {
                "title": "Complete",
                "href": "https://example.com/complete",
                "body": "Body text",
            },
        ]

        result = await client.search("python")

        assert len(result["results"]) == 1
        assert result["results"][0]["content"] == "Body text"

    @pytest.mark.asyncio
    async def test_search_handles_duckduckgo_exception(self, client):
        client._mock_ddgs.text.side_effect = DDGSException("Search failed")

        result = await client.search("python")

        assert result == {"results": []}
        client._mock_ddgs.text.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_handles_unexpected_exception(self, client):
        client._mock_ddgs.text.side_effect = RuntimeError("Unexpected error")

        result = await client.search("python")

        assert result == {"results": []}
        client._mock_ddgs.text.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_does_not_raise(self, client):
        await client.close()  # Should not raise any exception
