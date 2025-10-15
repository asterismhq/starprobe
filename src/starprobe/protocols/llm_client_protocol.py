"""Protocol definition for language model client interface."""

from typing import Any, Protocol


class LLMClientProtocol(Protocol):
    """Protocol defining the interface for any LLM client implementation.

    This protocol allows for dependency injection and easier testing by defining a
    contract that both real and mock implementations must follow, regardless of the
    underlying provider.
    """

    async def invoke(self, messages: Any, **kwargs: Any) -> Any:
        """Generate a response from the LLM.

        Args:
            messages: The input messages to send to the LLM (can be a list of messages
                     or other format depending on the implementation)
            **kwargs: Additional keyword arguments for generation control

        Returns:
            The LLM response object containing the generated content
        """
        ...

    def bind_tools(self, tools: list[Any]) -> "LLMClientProtocol":
        """Bind tools to the LLM client for function calling.

        Args:
            tools: List of tool definitions to bind

        Returns:
            A new client instance with the tools bound
        """
        ...
