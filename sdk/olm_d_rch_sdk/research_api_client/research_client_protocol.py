from typing import Any, Dict, Protocol


class ResearchClientProtocol(Protocol):
    def research(self, topic: str) -> Dict[str, Any]: ...
