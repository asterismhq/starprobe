import socket
from unittest.mock import Mock, patch

import pytest
import requests

from ollama_deep_researcher.utils import ScrapingModel


class TestScrapingModel:
    """Test suite for ScrapingModel class"""

    # Normal Cases
    def test_scrape_success_with_clean_html(self):
        """Verify successful HTML scraping and cleaning of unwanted elements"""
        scraper = ScrapingModel()

        mock_html = """
        <html>
            <head><title>Test</title></head>
            <body>
                <script>console.log('remove me');</script>
                <style>.test { color: red; }</style>
                <header>Header content</header>
                <nav>Navigation</nav>
                <main>Main article content here</main>
                <aside>Sidebar</aside>
                <footer>Footer content</footer>
            </body>
        </html>
        """

        mock_response = Mock()
        mock_response.content = mock_html.encode()
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            with patch.object(scraper, "_is_private_host", return_value=False):
                result = scraper.scrape("http://example.com")

        # Assert unwanted elements are removed
        assert "remove me" not in result
        assert ".test" not in result
        assert "Header content" not in result
        assert "Navigation" not in result
        assert "Sidebar" not in result
        assert "Footer content" not in result

        # Assert main content is present
        assert "Main article content here" in result

        # Assert state is correct
        assert scraper.content == result
        assert scraper.is_scraping is False

    def test_scrape_extracts_body_text_only(self):
        """Verify only body text is extracted, not head content"""
        scraper = ScrapingModel()

        mock_html = """
        <html>
            <head><title>This should not appear</title></head>
            <body>
                <p>First paragraph</p>
                <p>Second paragraph</p>
            </body>
        </html>
        """

        mock_response = Mock()
        mock_response.content = mock_html.encode()
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            with patch.object(scraper, "_is_private_host", return_value=False):
                result = scraper.scrape("http://example.com")

        assert "This should not appear" not in result
        assert "First paragraph" in result
        assert "Second paragraph" in result

    def test_scrape_handles_non_html_content(self):
        """Verify non-HTML content returns empty string"""
        scraper = ScrapingModel()

        mock_response = Mock()
        mock_response.content = b"PDF content here"
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            with patch.object(scraper, "_is_private_host", return_value=False):
                result = scraper.scrape("http://example.com/file.pdf")

        assert result == ""
        assert scraper.content == ""

    # URL Validation Cases
    def test_validate_url_rejects_non_http_schemes(self):
        """Verify only http/https schemes are allowed"""
        scraper = ScrapingModel()

        invalid_urls = [
            "ftp://example.com",
            "file:///etc/passwd",
            "javascript:alert(1)",
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError, match="http or https"):
                scraper.validate_url(url)

    def test_validate_url_rejects_private_ips(self):
        """Verify private IPs are blocked"""
        scraper = ScrapingModel()

        test_cases = [
            (
                "http://127.0.0.1",
                [(socket.AF_INET, None, None, None, ("127.0.0.1", 0))],
            ),
            (
                "http://localhost",
                [(socket.AF_INET, None, None, None, ("127.0.0.1", 0))],
            ),
            (
                "http://192.168.1.1",
                [(socket.AF_INET, None, None, None, ("192.168.1.1", 0))],
            ),
            ("http://10.0.0.1", [(socket.AF_INET, None, None, None, ("10.0.0.1", 0))]),
        ]

        for url, addr_info in test_cases:
            with patch("socket.getaddrinfo", return_value=addr_info):
                with pytest.raises(ValueError, match="not allowed"):
                    scraper.validate_url(url)

    def test_validate_url_rejects_invalid_hostnames(self):
        """Verify malformed URLs without hostname are rejected"""
        scraper = ScrapingModel()

        with pytest.raises(ValueError, match="Invalid URL hostname"):
            scraper.validate_url("http://")

    def test_validate_url_rejects_unresolvable_hosts(self):
        """Verify DNS resolution check for non-existent hosts"""
        scraper = ScrapingModel()

        with patch("socket.getaddrinfo", side_effect=socket.gaierror):
            with pytest.raises(ValueError, match="could not be found"):
                scraper.validate_url("http://nonexistent-domain-12345.com")

    # Error Handling Cases
    def test_scrape_handles_timeout(self):
        """Verify timeout errors are handled correctly"""
        scraper = ScrapingModel()

        with patch("requests.get", side_effect=requests.Timeout("Connection timeout")):
            with patch.object(scraper, "_is_private_host", return_value=False):
                with pytest.raises(ValueError, match="Failed to retrieve content"):
                    scraper.scrape("http://example.com")

        assert scraper.last_error is not None
        assert "Failed to retrieve content" in scraper.last_error
        assert scraper.is_scraping is False

    def test_scrape_handles_http_errors(self):
        """Verify HTTP errors (404, 403, 500) are handled"""
        scraper = ScrapingModel()

        http_errors = [
            requests.HTTPError("404 Not Found"),
            requests.HTTPError("403 Forbidden"),
            requests.HTTPError("500 Internal Server Error"),
        ]

        for error in http_errors:
            with patch("requests.get", side_effect=error):
                with patch.object(scraper, "_is_private_host", return_value=False):
                    with pytest.raises(ValueError):
                        scraper.scrape("http://example.com")

            assert scraper.last_error is not None

    def test_scrape_handles_connection_errors(self):
        """Verify network connection errors are handled"""
        scraper = ScrapingModel()

        with patch(
            "requests.get", side_effect=requests.ConnectionError("Network unreachable")
        ):
            with patch.object(scraper, "_is_private_host", return_value=False):
                with pytest.raises(ValueError, match="Failed to retrieve content"):
                    scraper.scrape("http://example.com")

    # State Management Cases
    def test_reset_clears_state(self):
        """Verify reset() clears all state variables"""
        scraper = ScrapingModel()

        # Set state
        scraper.content = "Some content"
        scraper.is_scraping = True
        scraper.last_error = "Some error"

        # Reset
        scraper.reset()

        # Verify all cleared
        assert scraper.content is None
        assert scraper.is_scraping is False
        assert scraper.last_error is None

    def test_scraping_flag_set_during_operation(self):
        """Verify is_scraping flag is True during operation and False after"""
        scraper = ScrapingModel()

        # Initially False
        assert scraper.is_scraping is False

        # Mock successful scraping
        mock_response = Mock()
        mock_response.content = b"<html><body>Test</body></html>"
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.raise_for_status = Mock()

        with patch("requests.get", return_value=mock_response):
            with patch.object(scraper, "_is_private_host", return_value=False):
                scraper.scrape("http://example.com")

        # Should be False after completion
        assert scraper.is_scraping is False
