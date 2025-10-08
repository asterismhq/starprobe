from typing import Any, Dict, List, Optional

from ollama_deep_researcher.protocols.search_client_protocol import (
    SearchClientProtocol,
)


class MockSearchClient(SearchClientProtocol):
    """Mock implementation of the search client for testing purposes."""

    def __init__(self, mock_results: Optional[List[Dict[str, Any]]] = None):
        if mock_results is None:
            self.mock_results = [
                {
                    "title": "Mock Result 1",
                    "url": "https://example.com/mock1",
                    "content": "This is mock content for result 1.",
                    "raw_content": "This is mock content for result 1.",
                },
                {
                    "title": "Mock Result 2",
                    "url": "https://example.com/mock2",
                    "content": "This is mock content for result 2.",
                    "raw_content": "This is mock content for result 2.",
                },
                {
                    "title": "Mock Result 3",
                    "url": "https://example.com/mock3",
                    "content": "This is mock content for result 3.",
                    "raw_content": "This is mock content for result 3.",
                },
            ]
        else:
            self.mock_results = mock_results

    async def search(
        self, query: str, max_results: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        return {"results": self.mock_results[:max_results]}

    async def close(self) -> None:
        pass
