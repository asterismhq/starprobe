from functools import lru_cache

from fastapi import Depends
from nexus_sdk import MockNexusClient, NexusMLXClient, NexusOllamaClient

from .clients import DdgsClient
from .config import (
    AppSettings,
    DDGSSettings,
    NexusSettings,
    ScrapingSettings,
    WorkflowSettings,
)
from .protocols import DDGSClientProtocol, LLMClientProtocol, ScrapingServiceProtocol
from .services import PromptService, ResearchService, ScrapingService


@lru_cache()
def get_app_settings() -> AppSettings:
    return AppSettings()


@lru_cache()
def get_nexus_settings() -> NexusSettings:
    return NexusSettings()


@lru_cache()
def get_ddgs_settings() -> DDGSSettings:
    return DDGSSettings()


@lru_cache()
def get_scraping_settings() -> ScrapingSettings:
    return ScrapingSettings()


@lru_cache()
def get_workflow_settings() -> WorkflowSettings:
    return WorkflowSettings()


_BACKEND_CLIENTS: dict[str, type] = {
    "ollama": NexusOllamaClient,
    "mlx": NexusMLXClient,
}


def _create_llm_client(nexus_settings: NexusSettings) -> LLMClientProtocol:
    backend = nexus_settings.nexus_backend.lower()

    if nexus_settings.use_mock_nexus:
        return MockNexusClient(response_format="langchain", backend=backend)

    client_cls = _BACKEND_CLIENTS.get(backend)
    if client_cls is None:
        raise ValueError(f"Unsupported Nexus backend '{nexus_settings.nexus_backend}'")

    return client_cls(
        base_url=nexus_settings.nexus_base_url,
        response_format="langchain",
        timeout=nexus_settings.nexus_timeout,
    )


def get_llm_client(
    nexus_settings: NexusSettings = Depends(get_nexus_settings),
) -> LLMClientProtocol:
    return _create_llm_client(nexus_settings)


def _create_search_client(ddgs_settings: DDGSSettings) -> DDGSClientProtocol:
    if ddgs_settings.use_mock_search:
        from dev.mocks.mock_search_client import MockSearchClient

        return MockSearchClient()
    return DdgsClient(ddgs_settings)


def get_search_client(
    ddgs_settings: DDGSSettings = Depends(get_ddgs_settings),
) -> DDGSClientProtocol:
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


def _create_research_service(
    workflow_settings: WorkflowSettings,
    search_client: DDGSClientProtocol,
    scraping_service: ScrapingServiceProtocol,
) -> ResearchService:
    return ResearchService(workflow_settings, search_client, scraping_service)


def get_research_service(
    workflow_settings: WorkflowSettings = Depends(get_workflow_settings),
    search_client: DDGSClientProtocol = Depends(get_search_client),
    scraping_service: ScrapingServiceProtocol = Depends(get_scraping_service),
) -> ResearchService:
    return _create_research_service(workflow_settings, search_client, scraping_service)
