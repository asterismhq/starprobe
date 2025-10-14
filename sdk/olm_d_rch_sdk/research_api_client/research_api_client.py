import httpx

from .research_client_protocol import ResearchClientProtocol
from .schemas import ResearchResponse


class ResearchApiClient:
    def __init__(self, base_url: str, timeout: float = 300.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def research(self, topic: str) -> ResearchResponse:
        url = "/research"
        response = self._client.post(url, json={"query": topic})
        response.raise_for_status()
        return ResearchResponse(**response.json())


# Interface check
_: ResearchClientProtocol = ResearchApiClient(base_url="")
