from .app_settings import AppSettings
from .ddgs_settings import DDGSSettings
from .nexus_settings import NexusSettings
from .scraping_settings import ScrapingSettings
from .workflow_settings import WorkflowSettings

# Singleton instances
app_settings = AppSettings()
nexus_settings = NexusSettings()
ddgs_settings = DDGSSettings()
scraping_settings = ScrapingSettings()
workflow_settings = WorkflowSettings()

__all__ = [
    # Classes
    "BaseSettings",
    "NexusSettings",
    "DDGSSettings",
    "ScrapingSettings",
    "WorkflowSettings",
    "AppSettings",
    # Singletons
    "app_settings",
    "nexus_settings",
    "ddgs_settings",
    "scraping_settings",
    "workflow_settings",
]
