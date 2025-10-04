"""Ollama client with automatic switching between real and mock implementations."""

from typing import TYPE_CHECKING, Any, Optional

from ollama_deep_researcher.protocols.ollama_client_protocol import OllamaClientProtocol

if TYPE_CHECKING:
    from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


class OllamaClientAdapter(OllamaClientProtocol):
    """Adapter to make ChatOllama explicitly conform to OllamaClientProtocol."""

    def __init__(self, client: Any):
        self._client = client

    def invoke(self, messages: Any, **kwargs: Any) -> Any:
        return self._client.invoke(messages, **kwargs)

    def bind_tools(self, tools: list[Any]) -> OllamaClientProtocol:
        bound_client = self._client.bind_tools(tools)
        return OllamaClientAdapter(bound_client)


class OllamaClient(OllamaClientProtocol):
    """Ollama client that automatically switches between real and mock implementations."""

    def __init__(
        self,
        settings: "OllamaDeepResearcherSettings",
        base_url: str = "http://localhost:11434/",
        model: str = "llama3.2",
        temperature: float = 0,
        format: Optional[str] = None,
    ):
        """Initialize the Ollama client.

        Automatically chooses between MockOllamaClient and ChatOllama based on settings.debug.

        Args:
            settings: OllamaDeepResearcherSettings instance
            base_url: Base URL for the Ollama API
            model: Name of the LLM model to use
            temperature: Temperature setting for generation
            format: Output format (e.g., "json" for JSON mode)
        """
        if settings.debug:
            # Import here to avoid dependency in production
            from dev.mocks.mock_ollama_client import MockOllamaClient

            print("[DEBUG MODE] Using MockOllamaClient")
            self._client = MockOllamaClient(
                base_url=base_url, model=model, temperature=temperature, format=format
            )
        else:
            from langchain_ollama import ChatOllama

            kwargs = {
                "base_url": base_url,
                "model": model,
                "temperature": temperature,
            }
            if format is not None:
                kwargs["format"] = format

            self._client = OllamaClientAdapter(ChatOllama(**kwargs))

    def invoke(self, messages: Any, **kwargs: Any) -> Any:
        return self._client.invoke(messages, **kwargs)

    def bind_tools(self, tools: list[Any]) -> OllamaClientProtocol:
        return self._client.bind_tools(tools)
