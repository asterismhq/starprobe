from typing import Any, Dict, List, Protocol


class DDGSClientProtocol(Protocol):
    async def search(
        self, query: str, max_results: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]: ...

    async def close(self) -> None: ...
