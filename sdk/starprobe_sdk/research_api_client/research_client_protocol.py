from typing import Protocol

from .schemas import ResearchResponse


class ResearchClientProtocol(Protocol):
    def research(self, topic: str) -> ResearchResponse: ...
