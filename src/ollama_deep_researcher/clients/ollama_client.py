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
        model: str = "llama3.2:3b",
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
        self.settings = settings
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.format = format
        self._create_client()

    def _create_client(self):
        if self.settings.debug:
            # Import here to avoid dependency in production
            from dev.mocks.mock_ollama_client import MockOllamaClient

            print("[DEBUG MODE] Using MockOllamaClient")
            self._client = MockOllamaClient(
                base_url=self.base_url, model=self.model, temperature=self.temperature, format=self.format
            )
        else:
            from langchain_ollama import ChatOllama

            kwargs = {
                "base_url": self.base_url,
                "model": self.model,
                "temperature": self.temperature,
            }
            if self.format is not None:
                kwargs["format"] = self.format

            self._client = OllamaClientAdapter(ChatOllama(**kwargs))

    def configure(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        format: Optional[str] = None,
    ):
        """Configure the client with new parameters and recreate the internal client."""
        if base_url is not None:
            self.base_url = base_url
        if model is not None:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if format is not None:
            self.format = format
        self._create_client()

    def invoke(self, messages: Any, **kwargs: Any) -> Any:
        return self._client.invoke(messages, **kwargs)

    def configure(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        format: Optional[str] = None,
    ):
        """Configure the client with new parameters."""
        if base_url is not None:
            self.base_url = base_url
        if model is not None:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if format is not None:
            self.format = format
        # Note: For simplicity, we don't recreate the internal client here
        # In a real implementation, you might need to recreate ChatOllama
