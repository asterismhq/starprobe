from typing import Any, Dict, List

from src.ollama_deep_researcher.protocols.duckduckgo_client_protocol import DuckDuckGoClientProtocol


class MockDuckDuckGoClient(DuckDuckGoClientProtocol):
    """Mock implementation of DuckDuckGoClient for testing purposes."""

    def __init__(self, mock_results: List[Dict[str, Any]] = None):
        if mock_results is None:
            # Default mock results based on actual search output
            self.mock_results = [
                {
                    "title": "Mock Result 1",
                    "url": "https://example.com/mock1",
                    "content": "This is mock content for result 1.",
                    "raw_content": "This is mock content for result 1."
                },
                {
                    "title": "Mock Result 2",
                    "url": "https://example.com/mock2",
                    "content": "This is mock content for result 2.",
                    "raw_content": "This is mock content for result 2."
                },
                {
                    "title": "Mock Result 3",
                    "url": "https://example.com/mock3",
                    "content": "This is mock content for result 3.",
                    "raw_content": "This is mock content for result 3."
                }
            ]
        else:
            self.mock_results = mock_results

    def search(self, query: str, max_results: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Mock search method that returns predefined results.

        Args:
            query (str): The search query (ignored in mock)
            max_results (int, optional): Maximum number of results to return. Defaults to 3.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Mock search response with results
        """
        return {"results": self.mock_results[:max_results]}