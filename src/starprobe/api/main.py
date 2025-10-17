"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from importlib import metadata

from fastapi import FastAPI

from starprobe.api.logger import logger
from starprobe.api.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    logger.info("Starting olm-d-rch API service")
    yield
    logger.info("Shutting down olm-d-rch API service")


app = FastAPI(
    title="Ollama Deep Researcher API",
    description="Production-ready research agent API",
    version=metadata.version("starprobe"),
    lifespan=lifespan,
)

app.include_router(router)
