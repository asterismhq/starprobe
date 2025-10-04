from typing import TYPE_CHECKING, Any, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ollama_deep_researcher.clients.ollama_client import OllamaClient

if TYPE_CHECKING:
    from ollama_deep_researcher.clients.ollama_client import OllamaClient
    from ollama_deep_researcher.protocols.ollama_client_protocol import OllamaClientProtocol


class OllamaDeepResearcherSettings(BaseSettings):
    """The configurable fields for the research assistant."""

    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="ignore")

    max_web_research_loops: int = Field(
        default=3,
        validation_alias="MAX_WEB_RESEARCH_LOOPS",
        title="Research Depth",
        description="Number of research iterations to perform",
    )
    local_llm: str = Field(
        default="qwen3:4b",
        validation_alias="LLM_MODEL",
        title="LLM Model Name",
        description="Name of the LLM model to use",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434/",
        validation_alias="OLLAMA_BASE_URL",
        title="Ollama Base URL",
        description="Base URL for Ollama API",
    )
    strip_thinking_tokens: bool = Field(
        default=True,
        title="Strip Thinking Tokens",
        description="Whether to strip <think> tokens from model responses",
    )
    use_tool_calling: bool = Field(
        default=False,
        title="Use Tool Calling",
        description="Use tool calling instead of JSON mode for structured output",
    )
    debug: bool = Field(
        default=False,
        validation_alias="DEBUG",
        title="Debug Mode",
        description="Enable mock client mode for development and testing",
    )
    max_tokens_per_source: int = Field(
        default=1000,
        title="Max Tokens Per Source",
        description="Maximum number of tokens to include for each source's content",
    )

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "OllamaDeepResearcherSettings":
        """Create a Configuration instance from a RunnableConfig."""
        # Start with environment variables loaded by BaseSettings
        settings = cls()

        # Override with configurable values if provided
        if config and "configurable" in config:
            configurable = config["configurable"]
            for key, value in configurable.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)

        return settings


def get_config_value(value: Any) -> str:
    """
    Convert configuration values to string format, handling both string and enum types.

    Args:
        value (Any): The configuration value to process. Can be a string or an Enum.

    Returns:
        str: The string representation of the value.

    Examples:
        >>> get_config_value("tavily")
        'tavily'
        >>> get_config_value(SearchAPI.TAVILY)
        'tavily'
    """
    return value if isinstance(value, str) else value.value


