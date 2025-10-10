from typing import Any, Dict


class MockOllamaDeepResearcherClient:
    """A mock client for OllamaDeepResearcher for testing purposes."""

    def research(self, topic: str) -> Dict[str, Any]:
        """Mocks a research call and returns a sample dictionary."""
        return {
            "success": True,
            "summary": f"This is a mock research summary for the topic: {topic}",
            "sources": ["https://example.com/source1", "https://example.com/source2"],
            "error_message": None,
            "diagnostics": [],
            "processing_time": 0.1,
        }
