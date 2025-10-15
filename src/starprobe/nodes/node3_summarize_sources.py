import logging

from starprobe.protocols.llm_client_protocol import LLMClientProtocol
from starprobe.services.prompt_service import PromptService
from starprobe.services.text_processing_service import (
    TextProcessingService,
)


async def summarize_sources(
    research_topic: str,
    running_summary: str,
    web_research_results: list[str],
    prompt_service: PromptService,
    llm_client: LLMClientProtocol,
):
    """LangGraph node that summarizes web research results.

    Uses an LLM to create or update a running summary based on the newest web research
    results, integrating them with any existing summary.
    Includes error handling to ensure graceful degradation.

    Args:
        research_topic: The topic being researched
        running_summary: The current running summary
        web_research_results: List of web research results to summarize
        prompt_service: Service for generating prompts
        llm_client: Client for LLM interactions

    Returns:
        Dictionary with state update, including running_summary key containing the updated summary
    """
    logger = logging.getLogger(__name__)
    try:
        messages = prompt_service.generate_summarize_prompt(
            research_topic=research_topic,
            existing_summary=running_summary,
            new_context="\n".join(web_research_results),
        )
        result = await llm_client.invoke(messages)

        # Strip thinking tokens if configured
        running_summary = result.content
        if prompt_service.configurable.strip_thinking_tokens:
            running_summary = TextProcessingService.strip_thinking_tokens(
                running_summary
            )

        return {"running_summary": running_summary}
    except Exception as e:
        # Log error but preserve existing summary or return fallback
        message = f"Summarization error for topic '{research_topic}': {e}"
        logger.exception(
            "Summarization error",
            extra={
                "topic": research_topic,
                "has_context": bool(web_research_results),
                "error": str(e),
            },
        )
        return {
            "running_summary": running_summary or "Summary generation failed",
            "errors": [message],
        }
