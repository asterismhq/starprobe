"""Unit tests for DdgsClient."""

import pytest
from ddgs.exceptions import DDGSException

from ollama_deep_researcher.clients.ddgs_client import DdgsClient
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


@pytest.fixture
def settings():
    return OllamaDeepResearcherSettings(
        ollama_host="http://ollama:11434/",
        ollama_model="llama3.2:3b",
    )


@pytest.mark.asyncio
async def test_search_returns_results(settings, mocker):
    mock_ddgs_instance = mocker.Mock()
    mock_ddgs_instance.text.return_value = [
        {
            "title": "Example Result 1",
            "href": "https://example.com/1",
            "body": "Snippet 1",
        }
    ]

    mocker.patch(
        "ollama_deep_researcher.clients.ddgs_client.DDGS",
        return_value=mock_ddgs_instance,
    )
    client = DdgsClient(settings)
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
async def test_search_trims_to_max_results(settings, mocker):
    mock_ddgs_instance = mocker.Mock()
    all_results = [
        {
            "title": f"Result {idx}",
            "href": f"https://example.com/{idx}",
            "body": f"Snippet {idx}",
        }
        for idx in range(5)
    ]
    mock_ddgs_instance.text.side_effect = (
        lambda query, region=None, safesearch=None, max_results=3: all_results[
            :max_results
        ]
    )

    mocker.patch(
        "ollama_deep_researcher.clients.ddgs_client.DDGS",
        return_value=mock_ddgs_instance,
    )
    client = DdgsClient(settings)
    result = await client.search("python", max_results=2)

    assert len(result["results"]) == 2
    mock_ddgs_instance.text.assert_called_once_with(
        "python",
        region=settings.ddgs_region,
        safesearch=settings.ddgs_safesearch,
        max_results=2,
    )


@pytest.mark.asyncio
async def test_search_skips_incomplete_results(settings, mocker):
    mock_ddgs_instance = mocker.Mock()
    mock_ddgs_instance.text.return_value = [
        {"title": "Missing URL"},
        {"href": "https://example.com/1"},
        {
            "title": "Complete",
            "href": "https://example.com/complete",
            "body": "Body text",
        },
    ]

    mocker.patch(
        "ollama_deep_researcher.clients.ddgs_client.DDGS",
        return_value=mock_ddgs_instance,
    )
    client = DdgsClient(settings)
    result = await client.search("python")

    assert len(result["results"]) == 1
    assert result["results"][0]["content"] == "Body text"


@pytest.mark.asyncio
async def test_search_handles_duckduckgo_exception(settings, mocker):
    mock_ddgs_instance = mocker.Mock()
    mock_ddgs_instance.text.side_effect = DDGSException("Search failed")

    mocker.patch(
        "ollama_deep_researcher.clients.ddgs_client.DDGS",
        return_value=mock_ddgs_instance,
    )
    client = DdgsClient(settings)
    result = await client.search("python")

    assert result == {"results": []}
    mock_ddgs_instance.text.assert_called_once()


@pytest.mark.asyncio
async def test_search_handles_unexpected_exception(settings, mocker):
    mock_ddgs_instance = mocker.Mock()
    mock_ddgs_instance.text.side_effect = RuntimeError("Unexpected error")

    mocker.patch(
        "ollama_deep_researcher.clients.ddgs_client.DDGS",
        return_value=mock_ddgs_instance,
    )
    client = DdgsClient(settings)
    result = await client.search("python")

    assert result == {"results": []}
    mock_ddgs_instance.text.assert_called_once()


@pytest.mark.asyncio
async def test_close_does_not_raise(settings):
    client = DdgsClient(settings)
    await client.close()  # Should not raise any exception
