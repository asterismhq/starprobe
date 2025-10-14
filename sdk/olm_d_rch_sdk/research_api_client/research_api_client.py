from typing import Any, Dict

import httpx

from .research_client_protocol import ResearchClientProtocol


class ResearchApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def research(self, topic: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/research"
        response = httpx.post(url, json={"topic": topic}, timeout=300)
        response.raise_for_status()
        return response.json()


# Interface check
_: ResearchClientProtocol = ResearchApiClient(base_url="")
