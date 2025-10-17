from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_SUPPORTED_BACKENDS = {"ollama", "mlx"}


class NexusSettings(BaseSettings):
    """Settings for Nexus API configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    nexus_base_url: str = Field(
        default="http://localhost:8000",
        title="Nexus Base URL",
        description="Base URL for the Nexus API",
        alias="NEXUS_BASE_URL",
    )
    nexus_timeout: float = Field(
        default=30.0,
        title="Nexus Timeout",
        description="Request timeout in seconds for Nexus API calls",
        alias="NEXUS_TIMEOUT",
    )
    nexus_backend: str = Field(
        default="ollama",
        title="Nexus Backend",
        description="Target backend for Nexus requests (e.g., 'ollama' or 'mlx')",
        alias="STARPROBE_LLM_BACKEND",
    )
    use_mock_nexus: bool = Field(
        default=False,
        title="Use Mock Nexus Client",
        description="Use the mock Nexus client instead of the real implementation",
        alias="STARPROBE_USE_MOCK_NEXUS",
    )

    @field_validator("nexus_backend", mode="before")
    @classmethod
    def _normalise_backend(cls, value: str) -> str:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in _SUPPORTED_BACKENDS:
                return normalized
        raise ValueError("nexus_backend must be one of 'ollama' or 'mlx'.")
