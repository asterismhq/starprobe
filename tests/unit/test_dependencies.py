"""Unit tests for dependency injection providers."""

import pytest

from src.olm_d_rch.dependencies import (
    _create_llm_client,
    _create_prompt_service,
    _create_research_service,
    _create_scraping_service,
    _create_search_client,
    get_app_settings,
    get_ddgs_settings,
    get_scraping_settings,
    get_stl_conn_settings,
    get_workflow_settings,
)


class TestDependencyProviders:
    """Test cases for dependency injection provider functions."""

    def test_get_app_settings_returns_settings_instance(self):
        """Test that get_app_settings returns an AppSettings instance."""
        settings = get_app_settings()
        assert settings is not None
        # Should be cached
        settings2 = get_app_settings()
        assert settings is settings2

    def test_get_stl_conn_settings_returns_settings_instance(self):
        """Test that get_stl_conn_settings returns a StlConnSettings instance."""
        settings = get_stl_conn_settings()
        assert settings is not None
        # Should be cached
        settings2 = get_stl_conn_settings()
        assert settings is settings2

    def test_get_ddgs_settings_returns_settings_instance(self):
        """Test that get_ddgs_settings returns an DDGSSettings instance."""
        settings = get_ddgs_settings()
        assert settings is not None
        # Should be cached
        settings2 = get_ddgs_settings()
        assert settings is settings2

    def test_get_scraping_settings_returns_settings_instance(self):
        """Test that get_scraping_settings returns an ScrapingSettings instance."""
        settings = get_scraping_settings()
        assert settings is not None
        # Should be cached
        settings2 = get_scraping_settings()
        assert settings is settings2

    def test_get_workflow_settings_returns_settings_instance(self):
        """Test that get_workflow_settings returns an WorkflowSettings instance."""
        settings = get_workflow_settings()
        assert settings is not None
        # Should be cached
        settings2 = get_workflow_settings()
        assert settings is settings2

    def test_create_llm_client_returns_client(self):
        """Test that _create_llm_client returns an LLM client from stl-conn SDK."""
        stl_conn_settings = get_stl_conn_settings()
        client = _create_llm_client(stl_conn_settings)
        assert client is not None
        assert hasattr(client, "invoke")
        assert hasattr(client, "bind_tools")

    def test_create_search_client_returns_client(self):
        """Test that _create_search_client returns a search client."""
        ddgs_settings = get_ddgs_settings()
        client = _create_search_client(ddgs_settings)
        assert client is not None
        assert hasattr(client, "search")
        assert hasattr(client, "close")

    def test_create_scraping_service_returns_service(self):
        """Test that _create_scraping_service returns a scraping service."""
        scraping_settings = get_scraping_settings()
        service = _create_scraping_service(scraping_settings)
        assert service is not None
        assert hasattr(service, "validate_url")
        assert hasattr(service, "scrape")

    def test_create_prompt_service_returns_service(self):
        """Test that _create_prompt_service returns a PromptService instance."""
        workflow_settings = get_workflow_settings()
        service = _create_prompt_service(workflow_settings)
        assert service is not None
        assert hasattr(service, "generate_query_prompt")
        assert hasattr(service, "generate_summarize_prompt")
        assert hasattr(service, "generate_reflect_prompt")

    def test_create_research_service_returns_service(self):
        """Test that _create_research_service returns a ResearchService instance."""
        workflow_settings = get_workflow_settings()
        ddgs_settings = get_ddgs_settings()
        scraping_settings = get_scraping_settings()
        search_client = _create_search_client(ddgs_settings)
        scraping_service = _create_scraping_service(scraping_settings)
        service = _create_research_service(
            workflow_settings, search_client, scraping_service
        )
        assert service is not None
        assert hasattr(service, "search_and_scrape")

    @pytest.mark.parametrize("use_mock", [True, False])
    def test_create_llm_client_respects_mock_settings(self, monkeypatch, use_mock):
        """Test that _create_llm_client switches between mock and real based on settings."""
        if use_mock:
            monkeypatch.setenv("USE_MOCK_STL_CONN", "true")
        else:
            monkeypatch.setenv("USE_MOCK_STL_CONN", "false")
        get_stl_conn_settings.cache_clear()
        stl_conn_settings = get_stl_conn_settings()  # Re-get to pick up env change

        client = _create_llm_client(stl_conn_settings)
        assert client is not None

    @pytest.mark.parametrize("use_mock", [True, False])
    def test_create_search_client_respects_mock_settings(self, monkeypatch, use_mock):
        """Test that _create_search_client switches between mock and real based on settings."""
        if use_mock:
            monkeypatch.setenv("USE_MOCK_SEARCH", "true")
        else:
            monkeypatch.setenv("USE_MOCK_SEARCH", "false")
        get_ddgs_settings.cache_clear()
        ddgs_settings = get_ddgs_settings()
        client = _create_search_client(ddgs_settings)
        assert client is not None

    @pytest.mark.parametrize("use_mock", [True, False])
    def test_create_scraping_service_respects_mock_settings(
        self, monkeypatch, use_mock
    ):
        """Test that _create_scraping_service switches between mock and real based on settings."""
        if use_mock:
            monkeypatch.setenv("USE_MOCK_SCRAPING", "true")
        else:
            monkeypatch.setenv("USE_MOCK_SCRAPING", "false")
        get_scraping_settings.cache_clear()
        scraping_settings = get_scraping_settings()
        service = _create_scraping_service(scraping_settings)
        assert service is not None
