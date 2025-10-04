"""Root-level pytest fixtures for all tests."""

import pytest

from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


@pytest.fixture
def settings():
    """Provide OllamaDeepResearcherSettings instance for tests.

    Returns:
        OllamaDeepResearcherSettings: Settings instance with test configuration
    """
    return OllamaDeepResearcherSettings()
