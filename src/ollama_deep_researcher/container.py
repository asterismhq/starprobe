import sys
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Type, TypeVar

from ollama_deep_researcher.clients import DdgsClient, OllamaClient
from ollama_deep_researcher.config import (
    DDGSSettings,
    OllamaSettings,
    ScrapingSettings,
    WorkflowSettings,
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


MockType = TypeVar("MockType")


class DependencyContainer:
    """Container for managing dependencies based on settings."""

    def __init__(self):
        # Instantiate settings with current environment variables
        self.workflow_settings = WorkflowSettings()
        self.ollama_settings = OllamaSettings()
        self.ddgs_settings = DDGSSettings()
        self.scraping_settings = ScrapingSettings()

        self.ollama_client = self._create_ollama_client()
        self.search_client = self._create_search_client()
        self.scraping_service = self._create_scraping_service()

        # Instantiate services
        self.prompt_service = PromptService(self.workflow_settings)
        self.search_service = SearchService(self.search_client)
        self.research_service = ResearchService(
            self.workflow_settings, self.search_service, self.scraping_service
        )

    def _ensure_repo_root_on_path(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))

    def _import_mock_class(self, module_name: str, class_name: str) -> Type[MockType]:
        self._ensure_repo_root_on_path()
        module = import_module(module_name)
        return getattr(module, class_name)

    def _create_ollama_client(self) -> "OllamaClientProtocol":
        if self.ollama_settings.use_mock_ollama:
            try:
                MockOllamaClient = self._import_mock_class(
                    "dev.mocks.mock_ollama_client", "MockOllamaClient"
                )
                return MockOllamaClient()
            except (ImportError, AttributeError):
                pass
        return OllamaClient(self.ollama_settings)

    def _create_search_client(self) -> "SearchClientProtocol":
        if self.ddgs_settings.use_mock_search:
            try:
                MockSearchClient = self._import_mock_class(
                    "dev.mocks.mock_search_client", "MockSearchClient"
                )
                return MockSearchClient()
            except (ImportError, AttributeError):
                pass
        return DdgsClient(self.ddgs_settings)

    def _create_scraping_service(self) -> "ScrapingServiceProtocol":
        if self.scraping_settings.use_mock_scraping:
            try:
                MockScrapingService = self._import_mock_class(
                    "dev.mocks.mock_scraping_service", "MockScrapingService"
                )
                return MockScrapingService()
            except (ImportError, AttributeError):
                pass
        return ScrapingService(self.scraping_settings)

    # ...existing code...
