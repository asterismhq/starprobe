import logging

from .research_client_protocol import ResearchClientProtocol
from .schemas import ResearchResponse


class MockResearchApiClient:
    def research(self, topic: str) -> ResearchResponse:
        logging.info(f"Mock research called with: {topic}")
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
        return ResearchResponse(
            success=True,
            article=article,
            metadata=metadata,
            error_message=None,
            diagnostics=[],
            processing_time=0.1,
        )


# Interface check
_: ResearchClientProtocol = MockResearchApiClient()
