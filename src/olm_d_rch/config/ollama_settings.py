from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    """Settings for Ollama configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    ollama_model: str = Field(
        default="llama3.2:3b",
        title="Ollama Model Name",
        description="Name of the Ollama model to use",
        alias="OLM_D_RCH_OLLAMA_MODEL",
    )
    ollama_host: Optional[str] = Field(
        default=None,
        title="Ollama Host",
        description="Base URL for the Ollama instance",
        alias="OLLAMA_HOST",
    )
    use_mock_ollama: bool = Field(
        default=False,
        title="Use Mock Ollama Client",
        description="Use the mock Ollama client instead of the real implementation",
        alias="USE_MOCK_OLLAMA",
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

    @field_validator("use_mock_ollama", mode="before")
    @classmethod
    def parse_bool_flags(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @field_validator("ollama_model", mode="before")
    @classmethod
    def normalize_ollama_model(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return "llama3.2:3b"
        return value

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "OllamaSettings":
        """Create an OllamaSettings instance from a RunnableConfig."""
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
