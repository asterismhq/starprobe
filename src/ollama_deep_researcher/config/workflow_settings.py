from typing import TYPE_CHECKING, Any, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    pass


class WorkflowSettings(BaseSettings):
    """The configurable fields for the research assistant workflow."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    max_web_research_loops: int = Field(
        default=3,
        title="Research Depth",
        description="Number of research iterations to perform",
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
        alias="RESEARCH_API_DEBUG",
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
    ) -> "WorkflowSettings":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = config.get("configurable", {}) if config else {}

        init_kwargs: dict[str, Any] = {}
        # Note: ollama_host and ollama_model are now handled by OllamaSettings

        # Start with environment variables loaded by BaseSettings, allowing
        # required values to be provided through the configurable section.
        settings = cls(**init_kwargs)

        # Override with configurable values if provided
        for key, value in configurable.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        return settings
