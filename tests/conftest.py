"""Root-level pytest fixtures for all tests."""

import pytest

from dev.mocks.mock_mlx_client import MockMLXClient
from dev.mocks.mock_ollama_client import MockOllamaClient
from dev.mocks.mock_scraping_service import MockScrapingService
from dev.mocks.mock_search_client import MockSearchClient


@pytest.fixture
def mock_search_client():
    """Mock search client for testing."""
    return MockSearchClient()


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for testing."""
    return MockOllamaClient()


@pytest.fixture
def mock_mlx_client():
    """Mock MLX client for testing."""
    return MockMLXClient()


@pytest.fixture
def mock_scraping_service():
    """Mock scraping service for testing."""
    return MockScrapingService()
