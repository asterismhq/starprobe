"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from importlib import metadata

from fastapi import FastAPI

from starprobe.api.logger import logger
from starprobe.api.router import router


def get_app_version(package_name: str, fallback_version: str = "0.1.0") -> str:
    """
    Safely retrieve the package version.

    Args:
        package_name: Package name (e.g., "starprobe")
        fallback_version: Default version to use when retrieval fails

    Returns:
        Version string
    """
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        logger.warning(
            f"Package '{package_name}' not found, using fallback version '{fallback_version}'"
        )
        return fallback_version


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    logger.info("Starting olm-d-rch API service")
    yield
    logger.info("Shutting down olm-d-rch API service")


app = FastAPI(
    title="Ollama Deep Researcher API",
    description="Production-ready research agent API",
    version=get_app_version("starprobe"),
    lifespan=lifespan,
)

app.include_router(router)
