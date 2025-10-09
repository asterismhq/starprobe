"""Unit tests for SearXNGClient."""

import httpx
import pytest

from ollama_deep_researcher.clients.searxng_client import SearXNGClient
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


@pytest.fixture
def settings():
    return OllamaDeepResearcherSettings(
        searxng_url="http://searxng:8080",
        ollama_host="http://ollama:11434/",
        ollama_model="llama3.2:3b",
    )


@pytest.fixture
def client_factory(settings):
    async def _factory(payload, status_code: int = 200):
        def handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(status_code, json=payload)

        transport = httpx.MockTransport(handler)
        client = httpx.AsyncClient(
            base_url=settings.searxng_url.rstrip("/"),
            transport=transport,
        )
        return SearXNGClient(settings, client=client)

    return _factory


@pytest.mark.asyncio
async def test_search_returns_results(client_factory):
    payload = {
        "results": [
            {
                "title": "Example Result 1",
                "url": "https://example.com/1",
                "content": "Snippet 1",
            }
        ]
    }

    client = await client_factory(payload)
    result = await client.search("python")

    assert result == {
        "results": [
            {
                "title": "Example Result 1",
                "url": "https://example.com/1",
                "content": "Snippet 1",
                "raw_content": "Snippet 1",
            }
        ]
    }


@pytest.mark.asyncio
async def test_search_trims_to_max_results(client_factory):
    payload = {
        "results": [
            {
                "title": f"Result {idx}",
                "url": f"https://example.com/{idx}",
                "content": f"Snippet {idx}",
            }
            for idx in range(5)
        ]
    }

    client = await client_factory(payload)
    result = await client.search("python", max_results=2)

    assert len(result["results"]) == 2


@pytest.mark.asyncio
async def test_search_skips_incomplete_results(client_factory):
    payload = {
        "results": [
            {"title": "Missing URL"},
            {"url": "https://example.com/1"},
            {
                "title": "Complete",
                "url": "https://example.com/complete",
                "summary": "Summary text",
            },
        ]
    }

    client = await client_factory(payload)
    result = await client.search("python")

    assert len(result["results"]) == 1
    assert result["results"][0]["content"] == "Summary text"


@pytest.mark.asyncio
async def test_search_handles_http_errors(settings, mocker):
    httpx_client = mocker.AsyncMock()
    httpx_client.get.side_effect = httpx.RequestError("boom")
    client = SearXNGClient(settings, client=httpx_client)

    result = await client.search("python")

    assert result == {"results": []}
    httpx_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_search_handles_invalid_json(settings, mocker):
    response = mocker.Mock()
    response.raise_for_status.return_value = None
    response.json.side_effect = ValueError("not json")

    httpx_client = mocker.AsyncMock()
    httpx_client.get.return_value = response

    client = SearXNGClient(settings, client=httpx_client)

    result = await client.search("python")

    assert result == {"results": []}
    httpx_client.get.assert_called_once()
