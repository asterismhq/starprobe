from dev.mocks.mock_scraping_service import MockScrapingService
from olm_d_rch.config.scraping_settings import ScrapingSettings
from olm_d_rch.services import ScrapingService


def test_validate_url():
    """Test URL validation behavior matches between real and mock."""
    print("Testing URL validation:")
    real_service = ScrapingService(settings=ScrapingSettings())
    mock_service = MockScrapingService()

    test_urls = [
        ("https://example.com", True, "valid HTTPS URL"),
        ("http://example.com", True, "valid HTTP URL"),
        ("", False, "empty URL"),
        ("ftp://example.com", False, "invalid scheme (real only)"),
    ]

    for url, should_pass, description in test_urls:
        print(f"\n  Testing {description}: '{url}'")

        # Test real service
        real_passed = False
        try:
            real_service.validate_url(url)
            real_passed = True
            print("    Real: PASS")
        except ValueError as e:
            print(f"    Real: FAIL - {e}")

        # Test mock service
        mock_passed = False
        try:
            mock_service.validate_url(url)
            mock_passed = True
            print("    Mock: PASS")
        except ValueError as e:
            print(f"    Mock: FAIL - {e}")

        # For basic cases, check if behavior matches expectations
        if url in ("", "https://example.com", "http://example.com"):
            match = real_passed == mock_passed == should_pass
            print(f"    Behavior match: {match}")


def test_scrape_return_type():
    """Test that scrape returns the same type."""
    print("\n\nTesting scrape return type:")
    mock_service = MockScrapingService()

    result = mock_service.scrape("https://example.com")
    print(f"  Mock result type: {type(result)}")
    print(f"  Mock result is string: {isinstance(result, str)}")
    print(f"  Mock result content: '{result}'")


def test_scrape_with_custom_content():
    """Test mock with custom content."""
    print("\n\nTesting mock with custom content:")
    custom_content = "Custom test content for scraping"
    mock_service = MockScrapingService(mock_content=custom_content)

    result = mock_service.scrape("https://test.com")
    print(f"  Expected: '{custom_content}'")
    print(f"  Got: '{result}'")
    print(f"  Match: {result == custom_content}")


def test_scrape_tracking():
    """Test that mock tracks scraped URLs."""
    print("\n\nTesting URL tracking in mock:")
    mock_service = MockScrapingService()

    urls = [
        "https://example1.com",
        "https://example2.com",
        "https://example3.com",
    ]

    for url in urls:
        mock_service.scrape(url)

    print(f"  URLs scraped: {len(mock_service.scraped_urls)}")
    print(f"  Tracked URLs: {mock_service.scraped_urls}")
    print(f"  All URLs tracked: {mock_service.scraped_urls == urls}")


def test_interface_compatibility():
    """Test that mock and real service have the same interface."""
    print("\n\nTesting interface compatibility:")
    real_service = ScrapingService(settings=ScrapingSettings())
    mock_service = MockScrapingService()

    # Check methods exist
    methods = ["validate_url", "scrape"]

    for method in methods:
        real_has = hasattr(real_service, method)
        mock_has = hasattr(mock_service, method)
        print(f"  Method '{method}':")
        print(f"    Real has: {real_has}")
        print(f"    Mock has: {mock_has}")
        print(f"    Match: {real_has == mock_has}")


if __name__ == "__main__":
    print("=" * 60)
    print("SCRAPING SERVICE MOCK COMPATIBILITY TEST")
    print("=" * 60)

    test_validate_url()
    test_scrape_return_type()
    test_scrape_with_custom_content()
    test_scrape_tracking()
    test_interface_compatibility()

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
