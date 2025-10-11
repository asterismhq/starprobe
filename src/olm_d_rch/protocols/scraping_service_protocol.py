from typing import Protocol


class ScrapingServiceProtocol(Protocol):
    def validate_url(self, url: str) -> None:
        """Validate the given URL.

        Args:
            url: The URL to validate

        Raises:
            ValueError: If the URL is invalid or not allowed
        """
        ...

    def scrape(self, url: str, timeout=(30, 90)) -> str:
        """Scrape content from the given URL.

        Args:
            url: The URL to scrape
            timeout: Request timeout tuple (connect, read)

        Returns:
            The scraped text content

        Raises:
            ValueError: If scraping fails
        """
        ...
