"""Mock Ollama client for development and testing."""

from typing import Any

from ollama_deep_researcher.protocols.ollama_client_protocol import OllamaClientProtocol


class MockResponse:
    """Mock response object that mimics the structure of ChatOllama responses."""

    def __init__(self, content: str):
        """Initialize mock response with content.

        Args:
            content: The content string to return as the response
        """
        self.content = content
        self.tool_calls = []


class MockOllamaClient(OllamaClientProtocol):
    """Mock implementation of the OllamaClientProtocol protocol.

    This mock client returns predefined responses without making actual API calls,
    useful for development and testing without requiring a running Ollama server.
    """

    def __init__(self, **kwargs: Any):
        """Initialize the mock client.

        Args:
            **kwargs: Configuration parameters (ignored in mock)
        """
        self._bound_tools = []
        self.base_url = kwargs.get("base_url", "http://localhost:11434/")
        self.model = kwargs.get("model", "llama3.2:3b")
        self.temperature = kwargs.get("temperature", 0)
        self.format = kwargs.get("format")
        print("[MockOllamaClient] Initialized - Using mock responses")

    def invoke(self, messages: Any, **kwargs: Any) -> MockResponse:
        """Return a mock response instead of calling the actual API.

        Args:
            messages: Input messages (analyzed to provide contextual responses)
            **kwargs: Additional parameters (ignored in mock)

        Returns:
            MockResponse object with predefined content
        """
        # Provide different mock responses based on context
        message_str = str(messages).lower()

        if "query" in message_str or "search" in message_str:
            # Mock search query generation
            content = '{"query": "mock search query for testing", "rationale": "This is a mock query"}'
        elif "reflect" in message_str or "evaluation" in message_str:
            # Mock reflection/evaluation
            content = '{"reflection": "This is a mock reflection.", "evaluation": "continue", "rationale": "Mock evaluation for testing"}'
        elif "summary" in message_str or "summarize" in message_str:
            # Mock summary generation
            content = "This is a mock summary of the research. The mock client has generated this response for testing purposes without connecting to the actual Ollama API."
        else:
            # Default mock response
            content = "This is a mock response from MockOllamaClient. No actual API call was made."

        print(
            f"[MockOllamaClient] Returning mock response for message type: {type(messages)}"
        )
        return MockResponse(content=content)

    def bind_tools(self, tools: list[Any]) -> "MockOllamaClient":
        """Bind tools to the mock client (for compatibility).

        Args:
            tools: List of tool definitions

        Returns:
            Self for method chaining
        """
        self._bound_tools = tools
        print(f"[MockOllamaClient] Bound {len(tools)} tools (mock)")
        return self

    def configure(
        self,
        base_url: Any = None,
        model: Any = None,
        temperature: Any = None,
        format: Any = None,
    ):
        """Configure the mock client (for compatibility).

        Args:
            base_url: Base URL (ignored in mock)
            model: Model name (ignored in mock)
            temperature: Temperature (ignored in mock)
            format: Format (ignored in mock)
        """
        if base_url is not None:
            self.base_url = base_url
        if model is not None:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if format is not None:
            self.format = format
        print(f"[MockOllamaClient] Configured with model={model}, base_url={base_url}")
