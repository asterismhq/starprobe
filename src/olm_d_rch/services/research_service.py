import logging
from typing import Any, Dict, List

from olm_d_rch.config.workflow_settings import WorkflowSettings
from olm_d_rch.protocols.ddgs_client_protocol import (
    DDGSClientProtocol,
)
from olm_d_rch.protocols.scraping_service_protocol import (
    ScrapingServiceProtocol,
)
from olm_d_rch.services.text_processing_service import (
    TextProcessingService,
)


class ResearchService:
    """Service class for handling web research operations.

    Dependencies:
    - TextProcessingService: For formatting and deduplicating search results
    - SearchClientProtocol: For web search functionality
    - ScrapingServiceProtocol: For web scraping functionality
    - WorkflowSettings: For configuration
    """

    def __init__(
        self,
        settings: WorkflowSettings,
        search_client: DDGSClientProtocol,
        scraper: ScrapingServiceProtocol,
    ):
        self.settings = settings
        self.search_client = search_client
        self.scraper = scraper
        self.logger = logging.getLogger(__name__)

    async def search_and_scrape(
        self, query: str, loop_count: int
    ) -> tuple[str, str, list[str]]:
        """Perform web search and scraping, return formatted results, sources, and errors."""
        errors: list[str] = []

        try:
            # Step 1: Search the web
            search_results = await self._perform_search(query, loop_count)
        except Exception as exc:
            message = f"Primary search failed for '{query}': {exc}"
            self.logger.exception(message)
            errors.append(message)
            search_results = {"results": []}

        if not search_results.get("results"):
            fallback_query = self._build_fallback_query(query)
            errors.append(
                f"No results returned for '{query}'. Retrying with '{fallback_query}'."
            )
            self.logger.warning(errors[-1])
            try:
                search_results = await self._perform_search(fallback_query, loop_count)
            except Exception as exc:
                message = f"Fallback search failed for '{fallback_query}': {exc}"
                self.logger.exception(message)
                errors.append(message)
                search_results = {"results": []}

        offline_fallback = False
        if not search_results.get("results"):
            errors.append(
                "Search results were empty after fallback. Using offline fallback data."
            )
            self.logger.warning(errors[-1])
            search_results = self._build_offline_results(query)
            offline_fallback = True

        try:
            # Step 2: Instantiate scraper
            scraper = self.scraper

            # Step 3: Loop through results and scrape each URL
            if "results" in search_results and not offline_fallback:
                for result in search_results["results"]:
                    url = result.get("url")
                    if not url:
                        continue

                    # Try to scrape full content
                    try:
                        scraped_content = scraper.scrape(url)
                        # Step 4: On success, update raw_content with scraped text
                        if scraped_content:
                            result["raw_content"] = scraped_content
                    except Exception as e:
                        # On failure, log at debug level and fall back to snippet from search
                        # This is expected behavior (403, timeouts, etc.) so don't treat as error
                        self.logger.debug(
                            f"Scraping failed for {url}, using snippet: {e}"
                        )
                        # Use snippet from search engine as fallback
                        result["raw_content"] = result.get("content", "")
                        continue

            # Format results with scraped content using the new service
            search_str = TextProcessingService.deduplicate_and_format_sources(
                search_results,
                self.settings,
            )

            sources = TextProcessingService.format_sources(search_results)

            return search_str, sources, errors
        except Exception as e:
            # Log error but continue with empty results
            message = f"Web research error: {e}"
            self.logger.exception(message)
            errors.append(message)
            return "", "", errors

    async def _perform_search(self, query: str, loop_count: int):
        """Perform the actual search using the configured search backend."""
        return await self.search_client.search(query, max_results=3)

    def _build_fallback_query(self, query: str) -> str:
        """Create a deterministic fallback query based on the original one."""
        query = (query or "").strip() or "technology trends"
        return f"{query} latest developments"

    def _build_offline_results(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Provide deterministic fallback results when search is unavailable."""
        slug = "-".join(word.lower() for word in query.split()) or "research-overview"
        fallback_url = f"https://example.com/{slug or 'research-overview'}"
        summary = (
            f"This is an offline fallback summary for '{query}'. "
            "It indicates that live search results were unavailable at runtime. "
            "Review system connectivity or search engine configuration to restore live data."
        )

        return {
            "results": [
                {
                    "title": f"Fallback insights for {query or 'research'}",
                    "url": fallback_url,
                    "content": summary,
                    "raw_content": summary,
                }
            ]
        }
