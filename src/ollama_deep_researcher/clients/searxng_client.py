import logging
from typing import Any, Dict, List, Optional

import httpx

from ..protocols.search_client_protocol import SearchClientProtocol
from ..settings import OllamaDeepResearcherSettings

logger = logging.getLogger(__name__)


class SearXNGClient(SearchClientProtocol):
    """Client for performing web searches using a SearXNG instance."""

    def __init__(
        self,
        settings: OllamaDeepResearcherSettings,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.settings = settings
        base_url = settings.searxng_url.rstrip("/")
        timeout = httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0)
        headers = {"User-Agent": "Mozilla/5.0 (compatible; OllamaDeepResearcher/1.0)"}
        self._client = client or httpx.AsyncClient(
            base_url=base_url, timeout=timeout, headers=headers
        )

    async def search(
        self, query: str, max_results: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search the web using SearXNG and return formatted results."""
        params = {
            "q": query,
            "format": "json",
            "language": "auto",
            "safesearch": 0,
        }

        try:
            response = await self._client.get("/search", params=params)
            response.raise_for_status()
        except Exception as exc:  # pragma: no cover - logged for observability
            logger.error("Error querying SearXNG: %s", exc)
            return {"results": []}

        try:
            payload = response.json()
        except ValueError as exc:  # pragma: no cover - defensive guard
            logger.error("Invalid JSON from SearXNG: %s", exc)
            return {"results": []}

        formatted_results: List[Dict[str, Any]] = []
        for raw in payload.get("results", [])[:max_results]:
            title = raw.get("title") or raw.get("source")
            url = raw.get("url")
            content = raw.get("content") or raw.get("summary") or raw.get("snippet")

            if not url or not title:
                logger.debug("Skipping incomplete SearXNG result: %s", raw)
                continue

            formatted_results.append(
                {
                    "title": title,
                    "url": url,
                    "content": content or "",
                    "raw_content": content or "",
                }
            )

        return {"results": formatted_results}

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
