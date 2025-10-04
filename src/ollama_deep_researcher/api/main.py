"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from ollama_deep_researcher.api.logger import logger
from ollama_deep_researcher.api.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    logger.info("Starting ollama-deep-researcher API service")
    yield
    logger.info("Shutting down ollama-deep-researcher API service")


app = FastAPI(
    title="Ollama Deep Researcher API",
    description="Production-ready research agent API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)
