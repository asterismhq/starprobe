from typing import Protocol

class ScrapingModelProtocol(Protocol):
    def scrape(self, url: str, timeout: tuple = (30, 90)) -> str:
        ...