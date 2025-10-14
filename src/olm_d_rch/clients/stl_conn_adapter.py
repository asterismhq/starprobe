"""Thin wrapper to adapt stl-conn SDK client to LangChain interface.

The stl-conn SDK v1.1.0+ natively supports LangChain responses via response_format="langchain",
but we still need this wrapper to:
1. Serialize LangChain message objects to dicts
2. Provide the bind_tools() method that LangChain expects
"""

from typing import Any

from stl_conn_sdk.stl_conn_client import MockStlConnClient, StlConnClient


class StlConnLangChainAdapter:
    """Thin adapter for StlConnClient with LangChain interface compatibility."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self._client = StlConnClient(
            base_url=base_url, response_format="langchain", timeout=timeout
        )
        self._tools: list[Any] | None = None

    async def invoke(self, messages: Any, **_kwargs: Any):
        """Invoke the LLM with message serialization."""
        # Serialize LangChain message objects to dicts
        serialized_messages = self._serialize_messages(messages)
        # SDK expects {"input": messages} format
        return await self._client.invoke({"input": serialized_messages})

    def _serialize_messages(self, messages: Any) -> Any:
        """Convert LangChain message objects to dict format."""
        if not isinstance(messages, list):
            return messages

        serialized = []
        for msg in messages:
            if hasattr(msg, "type") and hasattr(msg, "content"):
                # LangChain message object
                serialized.append({"role": msg.type, "content": msg.content})
            elif isinstance(msg, dict):
                serialized.append(msg)
            else:
                # Fallback
                serialized.append({"role": "user", "content": str(msg)})
        return serialized

    def bind_tools(self, tools: list[Any]) -> "StlConnLangChainAdapter":
        """Bind tools for function calling (LangChain compatibility)."""
        self._tools = tools
        return self


class MockStlConnLangChainAdapter:
    """Mock adapter for testing with realistic JSON responses."""

    def __init__(self):
        self._client = MockStlConnClient(response_format="langchain")
        self._tools: list[Any] | None = None

    async def invoke(self, messages: Any, **_kwargs: Any):
        """Return a mock LangChain-compatible response with JSON content."""
        # Use the SDK mock but override content with JSON for testing
        from stl_conn_sdk.stl_conn_client.response import LangChainResponse

        # Return JSON that matches what our nodes expect
        mock_json_content = '{"query": "test query", "rationale": "test rationale"}'
        return LangChainResponse(
            content=mock_json_content,
            tool_calls=[],
            raw_output={"message": {"content": mock_json_content}},
            raw_response={"output": {"message": {"content": mock_json_content}}},
        )

    def bind_tools(self, tools: list[Any]) -> "MockStlConnLangChainAdapter":
        """Bind tools for function calling (LangChain compatibility)."""
        self._tools = tools
        return self
