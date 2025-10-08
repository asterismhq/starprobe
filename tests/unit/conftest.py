"""Unit test fixtures providing mock clients and services."""

import pytest

from dev.mocks.mock_duckduckgo_client import MockDuckDuckGoClient
from dev.mocks.mock_ollama_client import MockOllamaClient
from dev.mocks.mock_scraping_service import MockScrapingService


@pytest.fixture
def mock_settings(default_settings):
    """Provide test-specific settings.

    Returns:
        OllamaDeepResearcherSettings: Settings instance for unit tests
    """
    return default_settings


@pytest.fixture
def mock_ollama_client():
    """Provide MockOllamaClient instance.

    Returns:
        MockOllamaClient: Mock Ollama client from dev/mocks
    """
    return MockOllamaClient()


@pytest.fixture
def mock_duckduckgo_client():
    """Provide MockDuckDuckGoClient instance.

    Returns:
        MockDuckDuckGoClient: Mock DuckDuckGo client from dev/mocks
    """
    return MockDuckDuckGoClient()


@pytest.fixture
def mock_scraping_service():
    """Provide MockScrapingService instance.

    Returns:
        MockScrapingService: Mock scraping service from dev/mocks
    """
    return MockScrapingService()
