import logging
from typing import Any, Dict, List

from ..protocols.duckduckgo_client_protocol import DuckDuckGoClientProtocol


class DuckDuckGoClient(DuckDuckGoClientProtocol):
    """Client for performing web searches using DuckDuckGo."""

    def __init__(self):
        from ddgs import DDGS

        self._client = DDGS()

    def search(
        self, query: str, max_results: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search the web using DuckDuckGo and return formatted results.

        Uses the DDGS library to perform web searches through DuckDuckGo.

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
            with self._client as ddgs:
                results = []
                search_results = list(ddgs.text(query, max_results=max_results))

                for r in search_results:
                    url = r.get("href")
                    title = r.get("title")
                    content = r.get("body")

                    if not all([url, title, content]):
                        logging.warning(f"Incomplete result from DuckDuckGo: {r}")
                        continue

                    raw_content = content

                    # Add result to list
                    result = {
                        "title": title,
                        "url": url,
                        "content": content,
                        "raw_content": raw_content,
                    }
                    results.append(result)

                return {"results": results}
        except Exception as e:
            logging.error(f"Error in DuckDuckGo search: {str(e)}")
            logging.error(f"Full error details: {type(e).__name__}")
            return {"results": []}
