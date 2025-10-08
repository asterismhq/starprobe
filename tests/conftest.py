"""Root-level pytest fixtures for all tests."""

import pytest

from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


@pytest.fixture
def default_settings():
    """
    Provide a default OllamaDeepResearcherSettings instance for tests.
    By default, this runs in debug mode (uses mocks).
    """
    return OllamaDeepResearcherSettings(
        max_web_research_loops=3,
        local_llm="tinyllama:1.1b",
        ollama_host="http://ollama:11434/",
        strip_thinking_tokens=True,
        use_tool_calling=False,
        debug=True,
        max_tokens_per_source=1000,
        scraping_timeout_connect=30,
        scraping_timeout_read=90,
    )


@pytest.fixture
def prod_settings():
    """
    Provide settings instance with DEBUG=False for tests.
    This is useful for integration tests that need real clients.
    """
    return OllamaDeepResearcherSettings(
        max_web_research_loops=3,
        local_llm="tinyllama:1.1bs",
        ollama_host="http://ollama:11434/",
        strip_thinking_tokens=True,
        use_tool_calling=False,
        debug=False,
        max_tokens_per_source=1000,
        scraping_timeout_connect=30,
        scraping_timeout_read=90,
    )


@pytest.fixture
def settings_with_tool_calling(default_settings):
    """Provide settings with tool calling enabled."""
    default_settings.use_tool_calling = True
    return default_settings
