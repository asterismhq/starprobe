"""API routes for the application."""

import asyncio
import time

from fastapi import APIRouter, Depends

from olm_d_rch.api.logger import logger
from olm_d_rch.api.schemas import (
    HealthResponse,
    ResearchRequest,
    ResearchResponse,
)
from olm_d_rch.dependencies import (
    _create_llm_client,
    get_app_settings,
    get_mlx_settings,
    get_ollama_settings,
    get_prompt_service,
    get_research_service,
)
from olm_d_rch.graph import build_graph
from olm_d_rch.services import PromptService, ResearchService

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for load balancers."""
    return HealthResponse(status="ok")


@router.post("/research", response_model=ResearchResponse)
async def run_research(
    request: ResearchRequest,
    prompt_service: PromptService = Depends(get_prompt_service),
    research_service: ResearchService = Depends(get_research_service),
    app_settings=Depends(get_app_settings),
    ollama_settings=Depends(get_ollama_settings),
    mlx_settings=Depends(get_mlx_settings),
):
    """Execute deep research on a given topic."""
    start_time = time.time()
    backend = request.backend
    logger.info(
        "Research request received",
        extra={"query": request.query, "backend": backend or "default"},
    )

    try:
        # Create LLM client based on request backend
        llm_client = _create_llm_client(
            backend or app_settings.llm_backend,
            app_settings,
            ollama_settings,
            mlx_settings,
        )

        # Build graph with injected services
        graph = build_graph(
            prompt_service, research_service, llm_client, backend=backend
        )

        # Execute graph with timeout
        result = await asyncio.wait_for(
            graph.ainvoke({"research_topic": request.query}),
            timeout=300.0,  # 5-minute timeout
        )

        # Map graph output to API response
        response = ResearchResponse(
            success=result.get("success", False),
            article=result.get("article"),
            metadata=result.get("metadata"),
            error_message=result.get("error_message"),
            diagnostics=result.get("diagnostics", []),
            processing_time=time.time() - start_time,
        )

        logger.info(
            "Research completed",
            extra={
                "query": request.query,
                "success": response.success,
                "backend": backend or "default",
                "article_length": len(response.article) if response.article else 0,
                "error_message": response.error_message,
                "diagnostics": response.diagnostics,
                "processing_time": response.processing_time,
            },
        )

        return response

    except asyncio.TimeoutError:
        logger.error(
            "Research timeout",
            extra={"query": request.query, "backend": backend or "default"},
        )
        return ResearchResponse(
            success=False,
            article=None,
            metadata=None,
            error_message="Research request exceeded 5-minute timeout",
            processing_time=time.time() - start_time,
        )
    except Exception as e:
        logger.error(
            "Research failed",
            extra={
                "query": request.query,
                "backend": backend or "default",
                "error": str(e),
            },
        )
        return ResearchResponse(
            success=False,
            article=None,
            metadata=None,
            error_message=f"Internal error: {str(e)}",
            processing_time=time.time() - start_time,
        )
