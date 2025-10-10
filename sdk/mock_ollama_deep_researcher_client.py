class MockOllamaDeepResearcherClient:
    def research(self, topic: str) -> dict:
        return {
            "success": True,
            "summary": "This is a mock research summary for the topic: " + topic,
            "sources": ["https://example.com/source1", "https://example.com/source2"],
            "error_message": None,
            "diagnostics": [],
            "processing_time": 0.1,
        }
