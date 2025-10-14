from functools import lru_cache

from fastapi import Depends

from .clients import (
    DdgsClient,
    MockStlConnLangChainAdapter,
    StlConnLangChainAdapter,
)
from .config import (
    AppSettings,
    DDGSSettings,
    ScrapingSettings,
    StlConnSettings,
    WorkflowSettings,
)
from .protocols import LLMClientProtocol, ScrapingServiceProtocol, SearchClientProtocol
from .services import PromptService, ResearchService, ScrapingService


@lru_cache()
def get_app_settings() -> AppSettings:
    return AppSettings()


@lru_cache()
def get_stl_conn_settings() -> StlConnSettings:
    return StlConnSettings()


@lru_cache()
def get_ddgs_settings() -> DDGSSettings:
    return DDGSSettings()


@lru_cache()
def get_scraping_settings() -> ScrapingSettings:
    return ScrapingSettings()


@lru_cache()
def get_workflow_settings() -> WorkflowSettings:
    return WorkflowSettings()


def _create_llm_client(stl_conn_settings: StlConnSettings) -> LLMClientProtocol:
    if stl_conn_settings.use_mock_stl_conn:
        return MockStlConnLangChainAdapter()
    return StlConnLangChainAdapter(
        base_url=stl_conn_settings.stl_conn_base_url,
        timeout=stl_conn_settings.stl_conn_timeout,
    )


def get_llm_client(
    stl_conn_settings: StlConnSettings = Depends(get_stl_conn_settings),
) -> LLMClientProtocol:
    return _create_llm_client(stl_conn_settings)


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
