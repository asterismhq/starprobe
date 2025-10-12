from .app_settings import AppSettings
from .ddgs_settings import DDGSSettings
from .mlx_settings import MLXSettings
from .ollama_settings import OllamaSettings
from .scraping_settings import ScrapingSettings
from .workflow_settings import WorkflowSettings

# Singleton instances
app_settings = AppSettings()
ollama_settings = OllamaSettings()
mlx_settings = MLXSettings()
ddgs_settings = DDGSSettings()
scraping_settings = ScrapingSettings()
workflow_settings = WorkflowSettings()

__all__ = [
    # Classes
    "BaseSettings",
    "OllamaSettings",
    "MLXSettings",
    "DDGSSettings",
    "ScrapingSettings",
    "WorkflowSettings",
    "AppSettings",
    # Singletons
    "app_settings",
    "ollama_settings",
    "mlx_settings",
    "ddgs_settings",
    "scraping_settings",
    "workflow_settings",
]
