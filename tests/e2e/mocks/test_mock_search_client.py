from dev.mocks.mock_search_client import MockSearchClient
from olm_d_rch.clients.ddgs_client import DdgsClient
from olm_d_rch.config.ddgs_settings import DDGSSettings


async def test_real_client_with_mocked_ddgs(mocker):
    mock_ddgs_instance = mocker.Mock()
    mock_ddgs_instance.text.return_value = [
        {
            "title": "Example Result 1",
            "href": "https://example.com/1",
            "body": "Snippet 1",
        },
        {
            "title": "Example Result 2",
            "href": "https://example.com/2",
            "body": "Snippet 2",
        },
    ]

    mocker.patch(
        "olm_d_rch.clients.ddgs_client.DDGS",
        return_value=mock_ddgs_instance,
    )
    settings = DDGSSettings()
    search_client = DdgsClient(settings)

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
