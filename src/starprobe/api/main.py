"""FastAPI application entry point."""

from contextlib import asynccontextmanager

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
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)
