"""Unit tests for DDGS-related settings."""

import os

from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


class TestDdgsSettings:
    """Test cases for DuckDuckGo search settings."""

    def test_ddgs_default_values(self):
        """Test that DDGS settings have correct defaults."""
        settings = OllamaDeepResearcherSettings()

        assert settings.ddgs_region == "wt-wt"
        assert settings.ddgs_safesearch == "moderate"
        assert settings.ddgs_max_results == 10

    def test_ddgs_env_overrides(self):
        """Test that DDGS settings can be overridden via environment variables."""
        os.environ["DDGS_REGION"] = "us-en"
        os.environ["DDGS_SAFESEARCH"] = "strict"
        os.environ["DDGS_MAX_RESULTS"] = "20"

        settings = OllamaDeepResearcherSettings()

        assert settings.ddgs_region == "us-en"
        assert settings.ddgs_safesearch == "strict"
        assert settings.ddgs_max_results == 20

        # Cleanup
        del os.environ["DDGS_REGION"]
        del os.environ["DDGS_SAFESEARCH"]
        del os.environ["DDGS_MAX_RESULTS"]

    def test_searxng_attributes_removed(self):
        """Test that SearXNG-related attributes no longer exist."""
        settings = OllamaDeepResearcherSettings()

        assert not hasattr(settings, "searxng_container_url")
        assert not hasattr(settings, "searxng_secret")
