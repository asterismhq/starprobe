from ollama_deep_researcher.protocols.scraping_service_protocol import (
    ScrapingServiceProtocol,
)
from ollama_deep_researcher.protocols.search_client_protocol import (
    SearchClientProtocol,
)
from ollama_deep_researcher.services.text_processing_service import (
    TextProcessingService,
)
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


class ResearchService:
    """Service class for handling web research operations.

    Dependencies:
    - TextProcessingService: For formatting and deduplicating search results
    - SearchClientProtocol: For web search functionality
    - ScrapingServiceProtocol: For web scraping functionality
    - OllamaDeepResearcherSettings: For configuration
    """

    def __init__(
        self,
        settings: OllamaDeepResearcherSettings,
        search_client: SearchClientProtocol,
        scraper: ScrapingServiceProtocol,
    ):
        self.settings = settings
        self.search_client = search_client
        self.scraper = scraper

    def search_and_scrape(self, query: str, loop_count: int) -> tuple[str, str]:
        """Perform web search and scraping, return formatted results and sources."""
        try:
            # Step 1: Search the web
            search_results = self._perform_search(query, loop_count)

            # Step 2: Instantiate scraper
            scraper = self.scraper

            # Step 3: Loop through results and scrape each URL
            if "results" in search_results:
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
                        # On failure, log warning and keep snippet
                        print(f"Warning: Scraping failed for {url}: {str(e)}")
                        # Keep the existing content as fallback (snippet from search)
                        continue

            # Format results with scraped content using the new service
            search_str = TextProcessingService.deduplicate_and_format_sources(
                search_results,
                self.settings,
            )

            sources = TextProcessingService.format_sources(search_results)

            return search_str, sources
        except Exception as e:
            # Log error but continue with empty results
            print(f"Web research error: {str(e)}")
            return f"Search failed: {str(e)}", "Error fetching sources"

    def _perform_search(self, query: str, loop_count: int):
        """Perform the actual search using the configured search backend."""
        return self.search_client.search(query, max_results=3)
