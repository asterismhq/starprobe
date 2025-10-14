from typing import Protocol, Dict, Any


class ResearchClientProtocol(Protocol):
    def research(self, topic: str) -> Dict[str, Any]:
        ...
