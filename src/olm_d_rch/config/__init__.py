from .app_settings import AppSettings
from .ddgs_settings import DDGSSettings
from .scraping_settings import ScrapingSettings
from .stl_conn_settings import StlConnSettings
from .workflow_settings import WorkflowSettings

# Singleton instances
app_settings = AppSettings()
stl_conn_settings = StlConnSettings()
ddgs_settings = DDGSSettings()
scraping_settings = ScrapingSettings()
workflow_settings = WorkflowSettings()

__all__ = [
    # Classes
    "BaseSettings",
    "StlConnSettings",
    "DDGSSettings",
    "ScrapingSettings",
    "WorkflowSettings",
    "AppSettings",
    # Singletons
    "app_settings",
    "stl_conn_settings",
    "ddgs_settings",
    "scraping_settings",
    "workflow_settings",
]
