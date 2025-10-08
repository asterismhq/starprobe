from src.ollama_deep_researcher.container import DependencyContainer


class TestDependencyContainer:
    """Test cases for DependencyContainer."""

    def test_production_mode(self, prod_settings):
        """Test container in production mode (DEBUG=false)."""
        container = DependencyContainer(prod_settings)

        # Check that real implementations are used
        assert hasattr(container.ollama_client, "_client")
        # For real OllamaClient, _client should be OllamaClientAdapter
        assert hasattr(container.ollama_client._client, "invoke")

        # DuckDuckGoClient should have _client as DDGS
        assert hasattr(container.duckduckgo_client, "_client")
        # Check it's not MockDuckDuckGoClient
        assert not hasattr(container.duckduckgo_client._client, "mock_results")

        # ScrapingService should be real
        assert hasattr(container.scraping_service, "scrape")

    def test_debug_mode(self, default_settings):
        """Test container in debug mode (DEBUG=true)."""
        container = DependencyContainer(default_settings)

        # Check that mock implementations are used
        # MockOllamaClient does not have _client, it implements invoke directly
        assert hasattr(container.ollama_client, "invoke")

        # MockDuckDuckGoClient does not have _client, it implements search directly
        assert hasattr(container.duckduckgo_client, "search")
        assert hasattr(container.duckduckgo_client, "mock_results")

        # ScrapingService should be mock
        assert hasattr(container.scraping_service, "scrape")

    def test_services_initialization(self, prod_settings):
        """Test that services are properly initialized."""
        container = DependencyContainer(prod_settings)

        # Check services exist
        assert container.prompt_service is not None
        assert container.search_service is not None
        assert container.research_service is not None

        # Check service dependencies
        assert container.search_service.search_client is container.duckduckgo_client
        assert container.research_service.search_client is container.search_service
        assert container.research_service.scraper is container.scraping_service
