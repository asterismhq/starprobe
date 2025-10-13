from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MLXSettings(BaseSettings):
    """Settings for MLX configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    model: str = Field(
        default="mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit",
        title="MLX Model Name",
        description="Name of the MLX model to use",
        alias="MLX_MODEL",
    )
    temperature: float = Field(
        default=0.0,
        title="MLX Temperature",
        description="Sampling temperature for MLX models",
        alias="OLM_D_RCH_MLX_TEMPERATURE",
    )

    @field_validator("model", mode="before")
    @classmethod
    def normalize_model(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return "mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit"
        return value

    @field_validator("temperature", mode="before")
    @classmethod
    def parse_temperature(cls, value: Any) -> float:
        if value is None:
            return 0.0
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        return float(value)

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "MLXSettings":
        """Create an MLXSettings instance from a RunnableConfig."""
        configurable = config.get("configurable", {}) if config else {}

        init_kwargs: dict[str, Any] = {}
        for field in ("model", "temperature"):
            if field in configurable:
                init_kwargs[field] = configurable[field]

        settings = cls(**init_kwargs)

        for key, value in configurable.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        return settings
