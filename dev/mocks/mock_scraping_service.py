from olm_d_rch.protocols.scraping_service_protocol import (
    ScrapingServiceProtocol,
)


class MockScrapingService(ScrapingServiceProtocol):
    def __init__(self, mock_content: str = "Mock scraped content"):
        self.mock_content = mock_content
        self.scraped_urls: list[str] = []

    def validate_url(self, url: str) -> None:
        """Mock URL validation - always passes unless URL is empty."""
        if not url:
            raise ValueError("URL cannot be empty")

    def scrape(self, url: str, timeout=(30, 90)) -> str:
        """Mock scraping - returns predefined content."""
        self.validate_url(url)
        self.scraped_urls.append(url)
        return self.mock_content
