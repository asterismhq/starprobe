from typing import Any, Dict

from olm_d_rch_sdk.protocols.research_client_protocol import ResearchClientProtocol


class MockResearchApiClient:
    def research(self, topic: str) -> Dict[str, Any]:
        print(f"Mock research called with: {topic}")
        return {
            "summary": "This is a mock summary for the topic.",
            "queries": ["mock query 1", "mock query 2"],
            "urls": ["https://example.com/mock_url_1", "https://example.com/mock_url_2"],
        }


# Interface check
_: ResearchClientProtocol = MockResearchApiClient()
