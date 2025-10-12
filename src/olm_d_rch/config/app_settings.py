from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application-wide settings that control shared LLM behaviour."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    llm_backend: Literal["ollama", "mlx"] = Field(
        default="ollama",
        title="Default LLM Backend",
        description="Default LLM backend to use when none is specified",
        alias="OLM_D_RCH_LLM_BACKEND",
    )
    use_mock_ollama: bool = Field(
        default=False,
        title="Use Mock Ollama Client",
        description="Whether to use the mock Ollama client",
        alias="USE_MOCK_OLLAMA",
    )
    use_mock_mlx: bool = Field(
        default=False,
        title="Use Mock MLX Client",
        description="Whether to use the mock MLX client",
        alias="USE_MOCK_MLX",
    )

    @field_validator("use_mock_ollama", "use_mock_mlx", mode="before")
    @classmethod
    def parse_bool_flags(cls, value: Any) -> bool:
        if isinstance(value, str):
            return value.lower() in {"true", "1", "yes", "on"}
        return bool(value)
