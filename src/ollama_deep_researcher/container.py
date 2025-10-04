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
            from mock_duckduckgo_client import MockDuckDuckGoClient
            from mock_ollama_client import MockOllamaClient
            from mock_scraping_service import MockScrapingService

            self.ollama_client: OllamaClientProtocol = MockOllamaClient()
            self.duckduckgo_client: DuckDuckGoClientProtocol = MockDuckDuckGoClient()
            self.scraping_service: ScrapingServiceProtocol = MockScrapingService()
        else:
            # Use real implementations
            self.ollama_client: OllamaClientProtocol = OllamaClient(self.settings)
            self.duckduckgo_client: DuckDuckGoClientProtocol = DuckDuckGoClient(
                self.settings
            )
            self.scraping_service: ScrapingServiceProtocol = ScrapingService(
                self.settings
            )

        # Instantiate services
        self.prompt_service = PromptService(self.settings)
        self.search_service = SearchService(self.duckduckgo_client)
        self.research_service = ResearchService(
            self.settings, self.search_service, self.scraping_service
        )
