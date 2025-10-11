from .ddgs_settings import DDGSSettings
from .ollama_settings import OllamaSettings
from .scraping_settings import ScrapingSettings
from .workflow_settings import WorkflowSettings

# Singleton instances
ollama_settings = OllamaSettings()
ddgs_settings = DDGSSettings()
scraping_settings = ScrapingSettings()
workflow_settings = WorkflowSettings()

__all__ = [
    # Classes
    "BaseSettings",
    "OllamaSettings",
    "DDGSSettings",
    "ScrapingSettings",
    "WorkflowSettings",
    # Singletons
    "ollama_settings",
    "ddgs_settings",
    "scraping_settings",
    "workflow_settings",
]
