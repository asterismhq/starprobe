from .ollama_client_protocol import OllamaClientProtocol
from .scraping_service_protocol import ScrapingServiceProtocol
from .search_client_protocol import SearchClientProtocol

__all__ = [
    "SearchClientProtocol",
    "OllamaClientProtocol",
    "ScrapingServiceProtocol",
]
