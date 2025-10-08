import os
import sys
from typing import TYPE_CHECKING

from ollama_deep_researcher.clients import DuckDuckGoClient, OllamaClient
from ollama_deep_researcher.services import (
    PromptService,
    ResearchService,
    ScrapingService,
    SearchService,
)
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings

if TYPE_CHECKING:
    from ollama_deep_researcher.protocols import (
        DuckDuckGoClientProtocol,
        OllamaClientProtocol,
        ScrapingServiceProtocol,
    )


class DependencyContainer:
    """Container for managing dependencies based on settings."""

    def __init__(self, settings: OllamaDeepResearcherSettings):
        self.settings = settings

        if self.settings.debug:
            # Use mock implementations
            dev_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../dev")
            )
            mocks_path = os.path.join(dev_path, "mocks")
            if mocks_path not in sys.path:
                sys.path.insert(0, mocks_path)
            try:
                MockDuckDuckGoClient = __import__("mock_duckduckgo_client", fromlist=["MockDuckDuckGoClient"]).MockDuckDuckGoClient  # type: ignore
                MockOllamaClient = __import__("mock_ollama_client", fromlist=["MockOllamaClient"]).MockOllamaClient  # type: ignore
                MockScrapingService = __import__("mock_scraping_service", fromlist=["MockScrapingService"]).MockScrapingService  # type: ignore
            except ImportError as e:
                raise ImportError(f"Failed to import mock modules: {e}") from e

            self.ollama_client: OllamaClientProtocol = MockOllamaClient()
            self.duckduckgo_client: DuckDuckGoClientProtocol = MockDuckDuckGoClient()
            self.scraping_service: ScrapingServiceProtocol = MockScrapingService()
        else:
            # Use real implementations
            self.ollama_client: OllamaClientProtocol = OllamaClient(self.settings)
            self.duckduckgo_client: DuckDuckGoClientProtocol = DuckDuckGoClient()
            self.scraping_service: ScrapingServiceProtocol = ScrapingService(
                self.settings
            )

        # Instantiate services
        self.prompt_service = PromptService(self.settings)
        self.search_service = SearchService(self.duckduckgo_client)
        self.research_service = ResearchService(
            self.settings, self.search_service, self.scraping_service
        )
