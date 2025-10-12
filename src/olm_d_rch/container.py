import logging
import sys
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Type, TypeVar

from olm_d_rch.clients import DdgsClient, MLXClient, OllamaClient
from olm_d_rch.config import (
    AppSettings,
    DDGSSettings,
    MLXSettings,
    OllamaSettings,
    ScrapingSettings,
    WorkflowSettings,
)
from olm_d_rch.services import (
    PromptService,
    ResearchService,
    ScrapingService,
    SearchService,
)

if TYPE_CHECKING:
    from olm_d_rch.protocols import (
        LLMClientProtocol,
        ScrapingServiceProtocol,
        SearchClientProtocol,
    )


MockType = TypeVar("MockType")


class DependencyContainer:
    """Container for managing dependencies based on settings."""

    def __init__(self):
        # Instantiate settings with current environment variables
        self.settings = AppSettings()
        self.workflow_settings = WorkflowSettings()
        self.ollama_settings = OllamaSettings()
        self.mlx_settings = MLXSettings()
        self.ddgs_settings = DDGSSettings()
        self.scraping_settings = ScrapingSettings()

        self._ollama_client: Optional["LLMClientProtocol"] = None
        self._mlx_client: Optional["LLMClientProtocol"] = None

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

    def _create_mock_ollama_client(self) -> "LLMClientProtocol":
        MockOllamaClient = self._import_mock_class(
            "dev.mocks.mock_ollama_client", "MockOllamaClient"
        )
        return MockOllamaClient()

    def _create_mock_mlx_client(self) -> "LLMClientProtocol":
        MockMLXClient = self._import_mock_class(
            "dev.mocks.mock_mlx_client", "MockMLXClient"
        )
        return MockMLXClient(
            model=self.mlx_settings.mlx_model,
            temperature=self.mlx_settings.temperature,
        )

    def _get_or_create_ollama_client(self) -> "LLMClientProtocol":
        if self._ollama_client is None:
            self._ollama_client = OllamaClient(self.ollama_settings)
        return self._ollama_client

    def _get_or_create_mlx_client(self) -> "LLMClientProtocol":
        if self._mlx_client is None:
            self._mlx_client = MLXClient(self.mlx_settings)
        return self._mlx_client

    def ollama_client(self) -> "LLMClientProtocol":
        """Return a cached Ollama client."""
        return self._get_or_create_ollama_client()

    def mlx_client(self) -> "LLMClientProtocol":
        """Return a cached MLX client."""
        return self._get_or_create_mlx_client()

    def mock_ollama_client(self) -> "LLMClientProtocol":
        """Return a fresh mock Ollama client."""
        return self._create_mock_ollama_client()

    def mock_mlx_client(self) -> "LLMClientProtocol":
        """Return a fresh mock MLX client."""
        return self._create_mock_mlx_client()

    def provide_llm_client(self, backend: Optional[str] = None) -> "LLMClientProtocol":
        """Return an LLM client based on backend preference."""
        backend_to_use = (backend or self.settings.llm_backend or "ollama").lower()

        if backend_to_use == "mlx":
            if self.settings.use_mock_mlx:
                try:
                    return self._create_mock_mlx_client()
                except (ImportError, AttributeError):
                    logging.warning(
                        "Failed to import mock MLX client. Using real MLX client."
                    )
            return self._get_or_create_mlx_client()

        if backend_to_use != "ollama":
            logging.warning(
                "Unknown LLM backend '%s'. Falling back to Ollama.", backend_to_use
            )

        if self.settings.use_mock_ollama:
            try:
                return self._create_mock_ollama_client()
            except (ImportError, AttributeError):
                logging.warning(
                    "Failed to import mock Ollama client. Using real Ollama client."
                )
        return self._get_or_create_ollama_client()

    def _create_search_client(self) -> "SearchClientProtocol":
        if self.ddgs_settings.use_mock_search:
            try:
                MockSearchClient = self._import_mock_class(
                    "dev.mocks.mock_search_client", "MockSearchClient"
                )
                return MockSearchClient()
            except (ImportError, AttributeError):
                logging.warning(
                    "Failed to import mock Search client. Using real Search client."
                )
        return DdgsClient(self.ddgs_settings)

    def _create_scraping_service(self) -> "ScrapingServiceProtocol":
        if self.scraping_settings.use_mock_scraping:
            try:
                MockScrapingService = self._import_mock_class(
                    "dev.mocks.mock_scraping_service", "MockScrapingService"
                )
                return MockScrapingService()
            except (ImportError, AttributeError):
                logging.warning(
                    "Failed to import mock Scraping service. Using real Scraping service."
                )
        return ScrapingService(self.scraping_settings)
