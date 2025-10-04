import logging
from typing import Any, Dict, List

from langsmith import traceable

from ..protocols.duckduckgo_client_protocol import DuckDuckGoClientProtocol


class SearchService:
    """Service for performing web searches using a search client.

    Dependencies:
    - DuckDuckGoClientProtocol: For executing web searches
    """

    def __init__(self, search_client: DuckDuckGoClientProtocol):
        self.search_client = search_client

    @traceable
    def search(
        self, query: str, max_results: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search the web using the injected search client and return formatted results.

        Args:
            query (str): The search query to execute
            max_results (int, optional): Maximum number of results to return. Defaults to 3.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Search response containing:
                - results (list): List of search result dictionaries, each containing:
                    - title (str): Title of the search result
                    - url (str): URL of the search result
                    - content (str): Snippet/summary of the content
                    - raw_content (str or None): Initially same as content, to be populated later
        """
        try:
            return self.search_client.search(query, max_results)
        except Exception as e:
            logging.error(f"Error in search: {str(e)}")
            logging.error(f"Full error details: {type(e).__name__}")
            return {"results": []}
