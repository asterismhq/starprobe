"""Ollama client with automatic switching between real and mock implementations."""

from typing import TYPE_CHECKING, Any

from ollama_deep_researcher.protocols.ollama_client_protocol import OllamaClientProtocol

if TYPE_CHECKING:
    from ollama_deep_researcher.config.ollama_settings import OllamaSettings


class OllamaClientAdapter(OllamaClientProtocol):
    """Adapter to make ChatOllama explicitly conform to OllamaClientProtocol."""

    def __init__(self, client: Any):
        self._client = client

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        import asyncio

        return await asyncio.to_thread(self._client.invoke, messages, **kwargs)

    def bind_tools(self, tools: list[Any]) -> OllamaClientProtocol:
        bound_client = self._client.bind_tools(tools)
        return OllamaClientAdapter(bound_client)


class OllamaClient(OllamaClientProtocol):
    """Ollama client that automatically switches between real and mock implementations."""

    def __init__(
        self,
        settings: "OllamaSettings",
    ):
        """Initialize the Ollama client.

        Automatically chooses between MockOllamaClient and ChatOllama based on settings.debug.

        Args:
            settings: OllamaSettings instance
        """
        self.settings = settings
        self.base_url = (
            settings.ollama_host.rstrip("/") if settings.ollama_host else None
        )
        self.model = settings.ollama_model
        self.temperature = 0
        self.format = None

        from langchain_ollama import ChatOllama

        kwargs = {
            "base_url": settings.ollama_host,
            "model": self.model,
            "temperature": self.temperature,
        }
        if self.format is not None:
            kwargs["format"] = self.format

        self._client = OllamaClientAdapter(ChatOllama(**kwargs))

    def configure(
        self,
        settings: "OllamaSettings",
    ):
        """Configure the client with new settings and recreate the internal client."""
        self.settings = settings
        self.base_url = (
            settings.ollama_host.rstrip("/") if settings.ollama_host else None
        )
        self.model = settings.ollama_model
        self.temperature = 0
        self.format = None

        from langchain_ollama import ChatOllama

        kwargs = {
            "base_url": settings.ollama_host,
            "model": self.model,
            "temperature": self.temperature,
        }
        if self.format is not None:
            kwargs["format"] = self.format

        self._client = OllamaClientAdapter(ChatOllama(**kwargs))

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        return await self._client.invoke(messages, **kwargs)
