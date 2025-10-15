from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScrapingSettings(BaseSettings):
    """Settings for web scraping configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
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
    use_mock_scraping: bool = Field(
        default=False,
        title="Use Mock Scraping Service",
        description="Use the mock scraping service instead of the real implementation",
        alias="STARPROBE_USE_MOCK_SCRAPING",
    )
