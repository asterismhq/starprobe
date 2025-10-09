import httpx

from dev.mocks.mock_search_client import MockSearchClient
from ollama_deep_researcher.clients.searxng_client import SearXNGClient
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


async def test_real_client_with_mock_transport():
    payload = {
        "results": [
            {
                "title": "Example Result 1",
                "url": "https://example.com/1",
                "content": "Snippet 1",
            },
            {
                "title": "Example Result 2",
                "url": "https://example.com/2",
                "summary": "Snippet 2",
            },
        ]
    }

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    settings = OllamaDeepResearcherSettings(
        searxng_url="http://searxng:8080",
        ollama_host="http://ollama:11434/",
        ollama_model="llama3.2:3b",
    )
    client = httpx.AsyncClient(
        base_url=settings.searxng_url.rstrip("/"), transport=transport
    )
    search_client = SearXNGClient(settings, client=client)

    results = await search_client.search("python", max_results=2)

    assert len(results["results"]) == 2
    assert results["results"][0]["title"] == "Example Result 1"
    assert results["results"][1]["content"] == "Snippet 2"


async def test_mock_client_structure_matches():
    mock_client = MockSearchClient()
    results = await mock_client.search("python", max_results=2)

    assert len(results["results"]) == 2
    keys = set(results["results"][0].keys())
    assert keys == {"title", "url", "content", "raw_content"}
