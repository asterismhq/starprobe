import json
from typing import Any, Dict, Optional
from unittest.mock import Mock

import httpx
import pytest
from starprobe_sdk import MockResearchApiClient, ResearchApiClient, ResearchResponse


class DummyResponse(httpx.Response):
    def __init__(
        self,
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        url: str = "http://example.com/research",
    ):
        content = json.dumps(json_data or {}).encode()
        request = httpx.Request("POST", url)
        super().__init__(status_code=status_code, content=content, request=request)

    def json(self, **kwargs: Any) -> Dict[str, Any]:
        return json.loads(self.content.decode())


def test_research_api_client_posts_to_api(monkeypatch: pytest.MonkeyPatch):
    mock_client = Mock()
    mock_client.post.return_value = DummyResponse(
        json_data={
            "success": True,
            "article": "Test article",
            "metadata": {"sources": []},
            "error_message": None,
            "diagnostics": [],
            "processing_time": 1.0,
        },
        url="http://example.com/research",
    )

    def fake_client(*args, **kwargs):
        return mock_client

    monkeypatch.setattr(httpx, "Client", fake_client)

    client = ResearchApiClient(base_url="http://example.com")
    response = client.research(topic="test topic")

    mock_client.post.assert_called_once_with("/research", json={"query": "test topic"})
    assert isinstance(response, ResearchResponse)
    assert response.success is True


def test_mock_research_api_client_returns_static_payload():
    client = MockResearchApiClient()

    result = client.research("example topic")

    # Note: logging.info goes to stderr, but for simplicity, check the result
    assert isinstance(result, ResearchResponse)
    assert result.success
    assert result.article is not None
    assert result.metadata is not None
    assert result.error_message is None
    assert result.diagnostics == []
    assert result.processing_time == 0.1
