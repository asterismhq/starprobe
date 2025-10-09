import logging
from typing import Any, Dict, List

from ddgs import DDGS
from ddgs.exceptions import DDGSException

from ..protocols.search_client_protocol import SearchClientProtocol
from ..settings import OllamaDeepResearcherSettings

logger = logging.getLogger(__name__)


class DdgsClient(SearchClientProtocol):
    """Client for performing web searches using DuckDuckGo via the ddgs library."""

    def __init__(self, settings: OllamaDeepResearcherSettings) -> None:
        self.settings = settings
        self._ddgs = DDGS()

    async def search(
        self, query: str, max_results: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search the web using DuckDuckGo and return formatted results."""
        try:
            raw_results = list(self._ddgs.text(query, max_results=max_results))
        except DDGSException as exc:
            logger.error("Error querying DuckDuckGo: %s", exc)
            return {"results": []}
        except Exception as exc:  # pragma: no cover - defensive catch-all
            logger.error("Unexpected error during DuckDuckGo search: %s", exc)
            return {"results": []}

        formatted_results: List[Dict[str, Any]] = []
        for raw in raw_results:
            title = raw.get("title")
            url = raw.get("href")
            content = raw.get("body")

            if not url or not title:
                logger.debug("Skipping incomplete DuckDuckGo result: %s", raw)
                continue

            formatted_results.append(
                {
                    "title": title,
                    "url": url,
                    "content": content or "",
                    # Leave raw_content empty so ResearchService will scrape
                    "raw_content": "",
                }
            )

        return {"results": formatted_results}

    async def close(self) -> None:
        """Close the client. DDGS does not require explicit cleanup."""
        pass
