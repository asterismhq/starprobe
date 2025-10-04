"""Unit tests for ScrapingService."""

import pytest
import requests

from ollama_deep_researcher.services.scraping_service import ScrapingService


class TestScrapingService:
    """Test cases for ScrapingService."""

    @pytest.fixture
    def scraping_service(self):
        """Create a ScrapingService instance for testing."""
        return ScrapingService()

    def test_validate_url_valid_http(self, scraping_service):
        """Test validation with valid HTTP URL."""
        # Should not raise for valid HTTP URL
        scraping_service.validate_url("http://example.com")

    def test_validate_url_valid_https(self, scraping_service):
        """Test validation with valid HTTPS URL."""
        # Should not raise for valid HTTPS URL
        scraping_service.validate_url("https://example.com")

    def test_validate_url_invalid_scheme_ftp(self, scraping_service):
        """Test rejection of FTP scheme."""
        with pytest.raises(ValueError, match="URL must use http or https scheme"):
            scraping_service.validate_url("ftp://example.com")

    def test_validate_url_invalid_scheme_file(self, scraping_service):
        """Test rejection of file scheme."""
        with pytest.raises(ValueError, match="URL must use http or https scheme"):
            scraping_service.validate_url("file:///etc/passwd")

    def test_validate_url_no_hostname(self, scraping_service):
        """Test rejection of URL without hostname."""
        with pytest.raises(ValueError, match="Invalid URL hostname"):
            scraping_service.validate_url("https://")

    def test_validate_url_localhost(self, scraping_service):
        """Test rejection of localhost."""
        with pytest.raises(ValueError, match="The specified host is not allowed"):
            scraping_service.validate_url("http://localhost")

    def test_validate_url_private_ip_127(self, scraping_service):
        """Test rejection of 127.0.0.1."""
        with pytest.raises(ValueError, match="The specified host is not allowed"):
            scraping_service.validate_url("http://127.0.0.1")

    def test_validate_url_private_ip_192(self, scraping_service):
        """Test rejection of private IP 192.168.x.x."""
        with pytest.raises(ValueError, match="The specified host is not allowed"):
            scraping_service.validate_url("http://192.168.1.1")

    def test_validate_url_private_ip_10(self, scraping_service):
        """Test rejection of private IP 10.x.x.x."""
        with pytest.raises(ValueError, match="The specified host is not allowed"):
            scraping_service.validate_url("http://10.0.0.1")

    def test_validate_url_nonexistent_host(self, scraping_service, mocker):
        """Test handling of non-existent host."""
        import socket

        mocker.patch("socket.getaddrinfo", side_effect=socket.gaierror)
        with pytest.raises(ValueError, match="could not be found"):
            scraping_service.validate_url("http://thishostdoesnotexist12345.com")

    def test_scrape_success(self, scraping_service, mocker):
        """Test successful scraping of HTML content."""
        # Mock successful HTTP response
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = b"<html><body><p>Test content</p></body></html>"

        mocker.patch("requests.get", return_value=mock_response)

        result = scraping_service.scrape("https://example.com")

        assert isinstance(result, str)
        assert "Test content" in result

    def test_scrape_removes_script_tags(self, scraping_service, mocker):
        """Test that script tags are removed from scraped content."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = (
            b"<html><body><p>Visible</p><script>alert('hidden')</script></body></html>"
        )

        mocker.patch("requests.get", return_value=mock_response)

        result = scraping_service.scrape("https://example.com")

        assert "Visible" in result
        assert "alert" not in result
        assert "hidden" not in result

    def test_scrape_removes_style_tags(self, scraping_service, mocker):
        """Test that style tags are removed from scraped content."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = b"<html><body><p>Content</p><style>.class { color: red; }</style></body></html>"

        mocker.patch("requests.get", return_value=mock_response)

        result = scraping_service.scrape("https://example.com")

        assert "Content" in result
        assert "color" not in result

    def test_scrape_timeout_parameter(self, scraping_service, mocker):
        """Test that timeout parameter is passed correctly."""
        mock_get = mocker.patch("requests.get")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = b"<html><body>Content</body></html>"
        mock_get.return_value = mock_response

        timeout = (10, 30)
        scraping_service.scrape("https://example.com", timeout=timeout)

        # Verify timeout was passed to requests.get
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs["timeout"] == timeout

    def test_scrape_default_timeout(self, scraping_service, mocker):
        """Test default timeout when none specified."""
        mock_get = mocker.patch("requests.get")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = b"<html><body>Content</body></html>"
        mock_get.return_value = mock_response

        scraping_service.scrape("https://example.com")

        # Verify default timeout (30, 90) was used
        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs["timeout"] == (30, 90)

    def test_scrape_network_error(self, scraping_service, mocker):
        """Test handling of network errors."""
        mocker.patch(
            "requests.get", side_effect=requests.RequestException("Network error")
        )

        with pytest.raises(ValueError, match="Failed to retrieve content"):
            scraping_service.scrape("https://example.com")

    def test_scrape_http_error(self, scraping_service, mocker):
        """Test handling of HTTP errors (404, 500, etc)."""
        mock_response = mocker.Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

        mocker.patch("requests.get", return_value=mock_response)

        with pytest.raises(ValueError, match="Failed to retrieve content"):
            scraping_service.scrape("https://example.com")

    def test_scrape_non_html_content(self, scraping_service, mocker):
        """Test handling of non-HTML content types (images, PDFs, etc)."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.content = b"fake image data"

        mocker.patch("requests.get", return_value=mock_response)

        result = scraping_service.scrape("https://example.com/image.png")

        # Should return empty string for non-HTML content
        assert result == ""

    def test_scrape_no_body_tag(self, scraping_service, mocker):
        """Test handling of HTML without body tag."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = b"<html><p>No body tag</p></html>"

        mocker.patch("requests.get", return_value=mock_response)

        result = scraping_service.scrape("https://example.com")

        # Should return empty string when no body tag
        assert result == ""

    def test_scrape_user_agent_header(self, scraping_service, mocker):
        """Test that User-Agent header is set."""
        mock_get = mocker.patch("requests.get")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = b"<html><body>Content</body></html>"
        mock_get.return_value = mock_response

        scraping_service.scrape("https://example.com")

        # Verify User-Agent header was set
        call_kwargs = mock_get.call_args.kwargs
        assert "headers" in call_kwargs
        assert "User-Agent" in call_kwargs["headers"]
        assert "Mozilla" in call_kwargs["headers"]["User-Agent"]

    def test_scrape_with_settings_timeout(self, mocker):
        """Test that settings timeout is used when provided."""
        mock_settings = mocker.Mock()
        mock_settings.scraping_timeout_connect = 5
        mock_settings.scraping_timeout_read = 15

        scraping_service = ScrapingService(settings=mock_settings)

        mock_get = mocker.patch("requests.get")
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.content = b"<html><body>Content</body></html>"
        mock_get.return_value = mock_response

        scraping_service.scrape("https://example.com")

        # Verify settings timeout was used
        call_kwargs = mock_get.call_args.kwargs
        assert call_kwargs["timeout"] == (5, 15)
