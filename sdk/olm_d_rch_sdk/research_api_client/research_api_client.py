import httpx

from .research_client_protocol import ResearchClientProtocol
from .schemas import ResearchResponse


class ResearchApiClient:
    def __init__(self, base_url: str, timeout: float = 300.0):
        self.base_url = base_url
        self.timeout = timeout

    def research(self, topic: str) -> ResearchResponse:
        url = f"{self.base_url}/api/v1/research"
        response = httpx.post(url, json={"query": topic}, timeout=self.timeout)
        response.raise_for_status()
        return ResearchResponse(**response.json())


# Interface check
_: ResearchClientProtocol = ResearchApiClient(base_url="")
