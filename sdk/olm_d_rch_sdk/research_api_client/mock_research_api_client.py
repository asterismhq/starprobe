from typing import Any, Dict

from .research_client_protocol import ResearchClientProtocol


class MockResearchApiClient:
    def research(self, topic: str) -> Dict[str, Any]:
        print(f"Mock research called with: {topic}")
        article = (
            f"# Mock Research Article\n\n"
            f"## Summary\n"
            f"This is a mock research summary for the topic: {topic}."
        )
        metadata = {
            "sources": [
                "https://example.com/source1",
                "https://example.com/source2",
            ],
            "source_count": 2,
        }
        return {
            "success": True,
            "article": article,
            "metadata": metadata,
            "error_message": None,
            "diagnostics": [],
            "processing_time": 0.1,
        }


# Interface check
_: ResearchClientProtocol = MockResearchApiClient()
