import ipaddress
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class ScrapingService:
    def validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL must use http or https scheme.")
        if not parsed.hostname:
            raise ValueError("Invalid URL hostname.")
        if self._is_private_host(parsed.hostname):
            raise ValueError("The specified host is not allowed.")

    def _is_private_host(self, host: str) -> bool:
        addrs = set()
        for family in (socket.AF_INET, socket.AF_INET6):
            try:
                for info in socket.getaddrinfo(host, None, family):
                    addrs.add(info[4][0])
            except socket.gaierror:
                continue

        # If DNS resolution fails (fictional host)
        if not addrs:
            raise ValueError(
                f"The specified host '{host}' could not be found. Please check the URL."
            )

        for addr in addrs:
            ip = ipaddress.ip_address(addr.split("%")[0])
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
                or ip.is_unspecified
            ):
                return True
        return False

    def scrape(self, url: str, timeout=(30, 90)) -> str:
        self.validate_url(url)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(
                url, headers=headers, timeout=timeout, allow_redirects=False
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Failed to retrieve content: {e}") from e

        # Early return for obviously non-HTML responses
        ctype = (response.headers.get("Content-Type") or "").lower()
        if not ("html" in ctype or ctype.startswith("text/")):
            return ""

        soup = BeautifulSoup(response.content, "html.parser")
        for element in soup(["script", "style", "header", "footer", "nav", "aside"]):
            element.decompose()
        if soup.body:
            content = soup.body.get_text(separator=" ", strip=True)
        else:
            content = ""

        return content
