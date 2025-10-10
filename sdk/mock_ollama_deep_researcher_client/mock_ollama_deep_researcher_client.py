from typing import Any, Dict


class MockOllamaDeepResearcherClient:
    """A mock client for OllamaDeepResearcher for testing purposes."""

    def research(self, query: str) -> Dict[str, Any]:
        """Mocks a research call and returns a sample dictionary."""
        article = (
            f"# Mock Research Article\n\n"
            f"## Summary\n"
            f"This is a mock research summary for the query: {query}."
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
