"""Adapter to make stl-conn SDK client compatible with LangChain interface."""

from typing import Any

from stl_conn_sdk.stl_conn_client import MockStlConnClient, StlConnClient


class LangChainResponse:
    """Wrapper to provide LangChain-compatible response interface."""

    def __init__(self, content: str, tool_calls: list[dict[str, Any]] | None = None):
        self.content = content
        self.tool_calls = tool_calls or []


class StlConnLangChainAdapter:
    """Adapter that wraps StlConnClient to provide LangChain-compatible interface."""

    def __init__(self, base_url: str):
        self._client = StlConnClient(base_url=base_url)
        self._tools: list[Any] | None = None

    async def invoke(self, messages: Any, **_kwargs: Any) -> LangChainResponse:
        """Invoke the LLM and return a LangChain-compatible response."""
        # Convert LangChain messages to dict format if needed
        if isinstance(messages, list) and messages:
            serialized_messages = []
            for msg in messages:
                if hasattr(msg, "type") and hasattr(msg, "content"):
                    # LangChain message object
                    serialized_messages.append(
                        {"role": msg.type, "content": msg.content}
                    )
                elif isinstance(msg, dict):
                    # Already a dict
                    serialized_messages.append(msg)
                else:
                    # Fallback: convert to string
                    serialized_messages.append({"role": "user", "content": str(msg)})
        else:
            serialized_messages = messages

        input_data = {"input_data": {"input": serialized_messages}}
        result = await self._client.invoke(input_data)

        # Extract content from stl-conn response format
        output = result.get("output", {})
        if isinstance(output, dict):
            content = output.get("message", {}).get("content", "")
            tool_calls = output.get("message", {}).get("tool_calls", [])
        else:
            # Fallback if format is different
            content = str(output)
            tool_calls = []

        return LangChainResponse(content=content, tool_calls=tool_calls)

    def bind_tools(self, tools: list[Any]) -> "StlConnLangChainAdapter":
        """Bind tools for function calling."""
        self._tools = tools
        return self


class MockStlConnLangChainAdapter:
    """Mock adapter for testing."""

    def __init__(self):
        self._client = MockStlConnClient()
        self._tools: list[Any] | None = None

    async def invoke(self, _messages: Any, **_kwargs: Any) -> LangChainResponse:
        """Return a mock LangChain-compatible response."""
        # For testing, return a simple mock response
        mock_content = '{"query": "test query", "rationale": "test rationale"}'
        return LangChainResponse(content=mock_content, tool_calls=[])

    def bind_tools(self, tools: list[Any]) -> "MockStlConnLangChainAdapter":
        """Bind tools for function calling."""
        self._tools = tools
        return self
