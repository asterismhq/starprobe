import os
import sys
from typing import TYPE_CHECKING

from ollama_deep_researcher.clients import DdgsClient, OllamaClient
from ollama_deep_researcher.config import (
    ddgs_settings,
    ollama_settings,
    scraping_settings,
    workflow_settings,
)
from ollama_deep_researcher.services import (
    PromptService,
    ResearchService,
    ScrapingService,
    SearchService,
)

if TYPE_CHECKING:
    from ollama_deep_researcher.protocols import (
        OllamaClientProtocol,
        ScrapingServiceProtocol,
        SearchClientProtocol,
    )


class DependencyContainer:
    """Container for managing dependencies based on settings."""

    def __init__(self):
        if workflow_settings.debug:
            # Try to use mock implementations, fall back to real if not available
            dev_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../dev")
            )
            mocks_path = os.path.join(dev_path, "mocks")
            if mocks_path not in sys.path:
                sys.path.insert(0, mocks_path)
            try:
                MockSearchClient = __import__("mock_search_client", fromlist=["MockSearchClient"]).MockSearchClient  # type: ignore
                MockOllamaClient = __import__("mock_ollama_client", fromlist=["MockOllamaClient"]).MockOllamaClient  # type: ignore
                MockScrapingService = __import__("mock_scraping_service", fromlist=["MockScrapingService"]).MockScrapingService  # type: ignore
                self.ollama_client: OllamaClientProtocol = MockOllamaClient()
                self.search_client: SearchClientProtocol = MockSearchClient()
                self.scraping_service: ScrapingServiceProtocol = MockScrapingService()
            except ImportError:
                # Fall back to real implementations if mocks are not available
                self.ollama_client: OllamaClientProtocol = OllamaClient(ollama_settings)
                self.search_client: SearchClientProtocol = DdgsClient(ddgs_settings)
                self.scraping_service: ScrapingServiceProtocol = ScrapingService(
                    scraping_settings
                )
        else:
            # Use real implementations
            self.ollama_client: OllamaClientProtocol = OllamaClient(ollama_settings)
            self.search_client: SearchClientProtocol = DdgsClient(ddgs_settings)
            self.scraping_service: ScrapingServiceProtocol = ScrapingService(
                scraping_settings
            )

        # Instantiate services
        self.prompt_service = PromptService(workflow_settings)
        self.search_service = SearchService(self.search_client)
        self.research_service = ResearchService(
            workflow_settings, self.search_service, self.scraping_service
        )
