import json
from typing import Any, Dict

import httpx
import pytest

from sdk.olm_d_rch_sdk import MockResearchApiClient, ResearchApiClient


class DummyResponse(httpx.Response):
    def __init__(
        self,
        status_code: int = 200,
        json_data: Dict[str, Any] | None = None,
        url: str = "http://example.com/api/v1/research",
    ):
        content = json.dumps(json_data or {}).encode()
        request = httpx.Request("POST", url)
        super().__init__(status_code=status_code, content=content, request=request)

    def json(self, **kwargs: Any) -> Dict[str, Any]:
        return json.loads(self.content.decode())


def test_research_api_client_posts_to_api(monkeypatch: pytest.MonkeyPatch):
    captured = {}

    def fake_post(url: str, json: Dict[str, Any], timeout: int) -> httpx.Response:
        captured.update({"url": url, "json": json, "timeout": timeout})
        return DummyResponse(json_data={"result": "ok"}, url=url)

    monkeypatch.setattr(httpx, "post", fake_post)

    client = ResearchApiClient(base_url="http://example.com")
    response = client.research(topic="test topic")

    assert captured["url"] == "http://example.com/api/v1/research"
    assert captured["json"] == {"topic": "test topic"}
    assert captured["timeout"] == 300
    assert response == {"result": "ok"}


def test_mock_research_api_client_returns_static_payload(
    capsys: pytest.CaptureFixture[str],
):
    client = MockResearchApiClient()

    result = client.research("example topic")
    captured = capsys.readouterr()

    assert "Mock research called with: example topic" in captured.out
    assert result["success"]
    assert "article" in result
    assert result["metadata"] is not None
    assert result["error_message"] is None
    assert result["diagnostics"] == []
    assert result["processing_time"] == 0.1
