"""API routes for the application."""

import asyncio
import time

from fastapi import APIRouter

from ollama_deep_researcher.api.logger import logger
from ollama_deep_researcher.api.schemas import (
    HealthResponse,
    ResearchRequest,
    ResearchResponse,
)
from ollama_deep_researcher.graph import build_graph
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for load balancers."""
    return HealthResponse(status="ok")


@router.post("/api/v1/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    """Execute deep research on a given topic."""
    start_time = time.time()
    logger.info("Research request received", extra={"topic": request.topic})

    try:
        # Loading Settings from the Settings Class
        settings = OllamaDeepResearcherSettings()

        # Build graph with injected services
        graph = build_graph(settings)

        # Execute graph with timeout
        result = await asyncio.wait_for(
            graph.ainvoke({"research_topic": request.topic}),
            timeout=300.0,  # 5-minute timeout
        )

        # Map graph output to API response
        response = ResearchResponse(
            success=result.get("success", False),
            summary=result.get("running_summary"),
            sources=result.get("sources", []),
            error_message=result.get("error_message"),
            processing_time=time.time() - start_time,
        )

        logger.info(
            "Research completed",
            extra={
                "topic": request.topic,
                "success": response.success,
                "source_count": len(response.sources),
            },
        )

        return response

    except asyncio.TimeoutError:
        logger.error("Research timeout", extra={"topic": request.topic})
        return ResearchResponse(
            success=False,
            summary=None,
            sources=[],
            error_message="Research request exceeded 5-minute timeout",
            processing_time=time.time() - start_time,
        )
    except Exception as e:
        logger.error("Research failed", extra={"topic": request.topic, "error": str(e)})
        return ResearchResponse(
            success=False,
            summary=None,
            sources=[],
            error_message=f"Internal error: {str(e)}",
            processing_time=time.time() - start_time,
        )
