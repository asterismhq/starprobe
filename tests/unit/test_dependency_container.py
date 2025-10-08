import os

from src.ollama_deep_researcher.container import DependencyContainer
from src.ollama_deep_researcher.settings import OllamaDeepResearcherSettings


class TestDependencyContainer:
    """Test cases for DependencyContainer."""

    def test_production_mode(self):
        """Test container in production mode (DEBUG=false)."""
        os.environ["DEBUG"] = "False"
        settings = OllamaDeepResearcherSettings()
        container = DependencyContainer(settings)

        # Check that real implementations are used
        assert hasattr(container.ollama_client, "_client")
        # For real OllamaClient, _client should be OllamaClientAdapter
        assert hasattr(container.ollama_client._client, "invoke")

        # Search client should wrap an HTTPX client
        assert hasattr(container.search_client, "_client")
        # Check it's not the mock implementation
        assert not hasattr(container.search_client, "mock_results")

        # ScrapingService should be real
        assert hasattr(container.scraping_service, "scrape")

    def test_debug_mode(self):
        """Test container in debug mode (DEBUG=true)."""
        os.environ["DEBUG"] = "True"
        settings = OllamaDeepResearcherSettings()
        container = DependencyContainer(settings)

        # Check that mock implementations are used
        # MockOllamaClient does not have _client, it implements invoke directly
        assert hasattr(container.ollama_client, "invoke")

        # MockSearchClient exposes mock_results directly
        assert hasattr(container.search_client, "search")
        assert hasattr(container.search_client, "mock_results")

        # ScrapingService should be mock
        assert hasattr(container.scraping_service, "scrape")

    def test_services_initialization(self):
        """Test that services are properly initialized."""
        os.environ["DEBUG"] = "False"
        settings = OllamaDeepResearcherSettings()
        container = DependencyContainer(settings)

        # Check services exist
        assert container.prompt_service is not None
        assert container.search_service is not None
        assert container.research_service is not None

        # Check service dependencies
        assert container.search_service.search_client is container.search_client
        assert container.research_service.search_client is container.search_service
        assert container.research_service.scraper is container.scraping_service
