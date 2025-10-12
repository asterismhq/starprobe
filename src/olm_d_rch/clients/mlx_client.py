"""MLX client with automatic switching between real and mock implementations."""

from typing import TYPE_CHECKING, Any

from olm_d_rch.protocols.llm_client_protocol import LLMClientProtocol

if TYPE_CHECKING:
    from olm_d_rch.config.mlx_settings import MLXSettings


class MLXClientAdapter(LLMClientProtocol):
    """Adapter to make ChatMLX conform to LLMClientProtocol."""

    def __init__(self, client: Any):
        self._client = client

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        import asyncio

        return await asyncio.to_thread(self._client.invoke, messages, **kwargs)

    def bind_tools(self, tools: list[Any]) -> LLMClientProtocol:
        bound_client = self._client.bind_tools(tools)
        return MLXClientAdapter(bound_client)


class MLXClient(LLMClientProtocol):
    """MLX client that wraps ChatMLX for compatibility with the shared protocol."""

    def __init__(self, settings: "MLXSettings"):
        self.configure(settings)

    def configure(self, settings: "MLXSettings"):
        """Configure the client with new settings and recreate the internal client."""
        self.settings = settings
        self.model = settings.mlx_model
        self.temperature = settings.temperature

        from langchain_community.chat_models.mlx import ChatMLX

        kwargs = {
            "model": self.model,
            "temperature": self.temperature,
        }

        self._client = MLXClientAdapter(ChatMLX(**kwargs))

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        return await self._client.invoke(messages, **kwargs)
