from typing import TYPE_CHECKING, Any, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    pass


class OllamaDeepResearcherSettings(BaseSettings):
    """The configurable fields for the research assistant."""

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    max_web_research_loops: int = Field(
        default=3,
        title="Research Depth",
        description="Number of research iterations to perform",
    )
    ollama_model: str = Field(
        default="llama3.2:3b",
        title="Ollama Model Name",
        description="Name of the Ollama model to use",
        alias="RESEARCH_API_OLLAMA_MODEL",
    )
    ollama_host: Optional[str] = Field(
        default=None,
        title="Ollama Host",
        description="Base URL for the Ollama instance",
        alias="OLLAMA_HOST",
    )
    searxng_container_url: str = Field(
        default="http://searxng:8080",
        title="SearXNG Container URL",
        description="URL for the SearXNG instance in container",
        alias="SEARXNG_CONTAINER_URL",
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
        title="Debug Mode",
        description="Enable mock client mode for development and testing",
        alias="DEBUG",
    )
    max_tokens_per_source: int = Field(
        default=1000,
        title="Max Tokens Per Source",
        description="Maximum number of tokens to include for each source's content",
    )
    scraping_timeout_connect: int = Field(
        default=30,
        title="Scraping Connect Timeout",
        description="Timeout in seconds for establishing connection during scraping",
    )
    scraping_timeout_read: int = Field(
        default=90,
        title="Scraping Read Timeout",
        description="Timeout in seconds for reading response during scraping",
    )

    @field_validator("ollama_host", mode="before")
    @classmethod
    def normalize_ollama_host(cls, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            trimmed = value.strip()
            if not trimmed:
                return None
            return trimmed.rstrip("/") + "/"
        return value

    @field_validator("ollama_model", mode="before")
    @classmethod
    def normalize_ollama_model(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return "llama3.2:3b"
        return value

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
        configurable = config.get("configurable", {}) if config else {}

        init_kwargs: dict[str, Any] = {}
        for field in ("ollama_host", "ollama_model"):
            if field in configurable:
                init_kwargs[field] = configurable[field]

        # Start with environment variables loaded by BaseSettings, allowing
        # required values to be provided through the configurable section.
        settings = cls(**init_kwargs)

        # Override with configurable values if provided
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
