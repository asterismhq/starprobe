from functools import lru_cache

from fastapi import Depends

from .clients import DdgsClient, MLXClient, OllamaClient
from .config import (
    AppSettings,
    DDGSSettings,
    MLXSettings,
    OllamaSettings,
    ScrapingSettings,
    WorkflowSettings,
)
from .protocols import LLMClientProtocol, ScrapingServiceProtocol, SearchClientProtocol
from .services import PromptService, ResearchService, ScrapingService, SearchService


@lru_cache()
def get_app_settings() -> AppSettings:
    return AppSettings()


@lru_cache()
def get_ollama_settings() -> OllamaSettings:
    return OllamaSettings()


@lru_cache()
def get_mlx_settings() -> MLXSettings:
    return MLXSettings()


@lru_cache()
def get_ddgs_settings() -> DDGSSettings:
    return DDGSSettings()


@lru_cache()
def get_scraping_settings() -> ScrapingSettings:
    return ScrapingSettings()


@lru_cache()
def get_workflow_settings() -> WorkflowSettings:
    return WorkflowSettings()


def _create_llm_client(
    settings: AppSettings,
    ollama_settings: OllamaSettings,
    mlx_settings: MLXSettings,
) -> LLMClientProtocol:
    # Include mock usage logic here
    if settings.use_mock_ollama:
        from dev.mocks.mock_ollama_client import MockOllamaClient

        return MockOllamaClient()
    if settings.use_mock_mlx:
        from dev.mocks.mock_mlx_client import MockMLXClient

        return MockMLXClient(
            model=mlx_settings.model,
            temperature=mlx_settings.temperature,
        )

    backend = settings.llm_backend.lower()
    factory = CLIENT_FACTORIES.get(backend)
    if factory:
        if backend == "ollama":
            return factory(ollama_settings)
        elif backend == "mlx":
            return factory(mlx_settings)
    # Default to ollama
    return OllamaClient(ollama_settings)


CLIENT_FACTORIES = {
    "ollama": lambda settings: OllamaClient(settings),
    "mlx": lambda settings: MLXClient(settings),
}


def get_llm_client(
    settings: AppSettings = Depends(get_app_settings),
    ollama_settings: OllamaSettings = Depends(get_ollama_settings),
    mlx_settings: MLXSettings = Depends(get_mlx_settings),
) -> LLMClientProtocol:
    return _create_llm_client(settings, ollama_settings, mlx_settings)


def _create_search_client(ddgs_settings: DDGSSettings) -> SearchClientProtocol:
    if ddgs_settings.use_mock_search:
        from dev.mocks.mock_search_client import MockSearchClient

        return MockSearchClient()
    return DdgsClient(ddgs_settings)


def get_search_client(
    ddgs_settings: DDGSSettings = Depends(get_ddgs_settings),
) -> SearchClientProtocol:
    return _create_search_client(ddgs_settings)


def _create_scraping_service(
    scraping_settings: ScrapingSettings,
) -> ScrapingServiceProtocol:
    if scraping_settings.use_mock_scraping:
        from dev.mocks.mock_scraping_service import MockScrapingService

        return MockScrapingService()
    return ScrapingService(scraping_settings)


def get_scraping_service(
    scraping_settings: ScrapingSettings = Depends(get_scraping_settings),
) -> ScrapingServiceProtocol:
    return _create_scraping_service(scraping_settings)


def _create_prompt_service(workflow_settings: WorkflowSettings) -> PromptService:
    return PromptService(workflow_settings)


def get_prompt_service(
    workflow_settings: WorkflowSettings = Depends(get_workflow_settings),
) -> PromptService:
    return _create_prompt_service(workflow_settings)


def _create_search_service(search_client: SearchClientProtocol) -> SearchService:
    return SearchService(search_client)


def get_search_service(
    search_client: SearchClientProtocol = Depends(get_search_client),
) -> SearchService:
    return _create_search_service(search_client)


def _create_research_service(
    workflow_settings: WorkflowSettings,
    search_client: SearchClientProtocol,
    scraping_service: ScrapingServiceProtocol,
) -> ResearchService:
    return ResearchService(workflow_settings, search_client, scraping_service)


def get_research_service(
    workflow_settings: WorkflowSettings = Depends(get_workflow_settings),
    search_client: SearchClientProtocol = Depends(get_search_client),
    scraping_service: ScrapingServiceProtocol = Depends(get_scraping_service),
) -> ResearchService:
    return _create_research_service(workflow_settings, search_client, scraping_service)
