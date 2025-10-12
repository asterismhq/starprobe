"""Mock MLX client for development and testing."""

from typing import Any

from olm_d_rch.protocols.llm_client_protocol import LLMClientProtocol


class MockMLXResponse:
    """Mock response object that mimics ChatMLX responses."""

    def __init__(self, content: str):
        self.content = content
        self.tool_calls = []


class MockMLXClient(LLMClientProtocol):
    """Mock implementation of the LLMClientProtocol protocol for MLX."""

    def __init__(self, **kwargs: Any):
        self._bound_tools: list[Any] = []
        self.model = kwargs.get("model", "mock-mlx-model")
        self.temperature = kwargs.get("temperature", 0)
        print("[MockMLXClient] Initialized - Using mock responses")

    async def invoke(self, messages: Any, **kwargs: Any) -> MockMLXResponse:
        message_str = str(messages).lower()

        if "query" in message_str or "search" in message_str:
            content = '{"query": "mock mlx query", "rationale": "Mock MLX response"}'
        elif "reflect" in message_str or "evaluation" in message_str:
            content = (
                '{"follow_up_query": "mock mlx follow-up", "knowledge_gap": "Mock"}'
            )
        elif "summary" in message_str or "summarize" in message_str:
            content = "This is a mock MLX summary generated for testing without real inference."
        else:
            content = "This is a generic mock response from MockMLXClient."

        print("[MockMLXClient] Returning mock response")
        return MockMLXResponse(content=content)

    def bind_tools(self, tools: list[Any]) -> "MockMLXClient":
        self._bound_tools = tools
        print(f"[MockMLXClient] Bound {len(tools)} tools (mock)")
        return self

    def configure(
        self,
        model: Any = None,
        temperature: Any = None,
    ) -> None:
        if model is not None:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
