"""Unit test fixtures providing mock clients and services."""

import pytest

from dev.mocks.mock_ollama_client import MockOllamaClient
from dev.mocks.mock_scraping_service import MockScrapingService
from dev.mocks.mock_search_client import MockSearchClient


@pytest.fixture
def mock_settings(default_settings):
    """Provide test-specific settings.

    Returns:
        OllamaDeepResearcherSettings: Settings instance for unit tests
    """
    # Override ollama_host for tests
    default_settings.ollama_host = "http://ollama:11434/"
    return default_settings


@pytest.fixture
def mock_ollama_client():
    """Provide MockOllamaClient instance.

    Returns:
        MockOllamaClient: Mock Ollama client from dev/mocks
    """
    return MockOllamaClient()


@pytest.fixture
def mock_search_client():
    """Provide MockSearchClient instance.

    Returns:
        MockSearchClient: Mock search client from dev/mocks
    """
    return MockSearchClient()


@pytest.fixture
def mock_scraping_service():
    """Provide MockScrapingService instance.

    Returns:
        MockScrapingService: Mock scraping service from dev/mocks
    """
    return MockScrapingService()
