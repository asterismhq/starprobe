from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DDGSSettings(BaseSettings):
    """Settings for DuckDuckGo search configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    ddgs_region: str = Field(
        default="wt-wt",
        title="DDGS Region",
        description="Region code for DuckDuckGo search (e.g., wt-wt for global, us-en for US)",
        alias="DDGS_REGION",
    )
    ddgs_safesearch: str = Field(
        default="moderate",
        title="DDGS SafeSearch",
        description="SafeSearch level for DuckDuckGo: off, moderate, or strict",
        alias="DDGS_SAFESEARCH",
    )
    ddgs_max_results: int = Field(
        default=10,
        title="DDGS Max Results",
        description="Maximum number of results to fetch from DuckDuckGo per query",
        alias="DDGS_MAX_RESULTS",
    )
    use_mock_search: bool = Field(
        default=False,
        title="Use Mock Search Client",
        description="Use the mock search client instead of the real implementation",
        alias="USE_MOCK_SEARCH",
    )
