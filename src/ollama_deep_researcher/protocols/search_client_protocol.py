from typing import Any, Dict, List, Protocol


class SearchClientProtocol(Protocol):
    def search(
        self, query: str, max_results: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]: ...
