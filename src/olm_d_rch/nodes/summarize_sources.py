import logging

from olm_d_rch.protocols.llm_client_protocol import LLMClientProtocol
from olm_d_rch.services.prompt_service import PromptService
from olm_d_rch.services.text_processing_service import (
    TextProcessingService,
)
from olm_d_rch.state import SummaryState


async def summarize_sources(
    state: SummaryState,
    prompt_service: PromptService,
    llm_client: LLMClientProtocol,
):
    """LangGraph node that summarizes web research results.

    Uses an LLM to create or update a running summary based on the newest web research
    results, integrating them with any existing summary.
    Includes error handling to ensure graceful degradation.

    Args:
        state: Current graph state containing research topic, running summary,
              and web research results
        prompt_service: Service for generating prompts
        llm_client: Client for LLM interactions

    Returns:
        Dictionary with state update, including running_summary key containing the updated summary
    """
    logger = logging.getLogger(__name__)
    try:
        messages = prompt_service.generate_summarize_prompt(
            research_topic=state.research_topic,
            existing_summary=state.running_summary,
            new_context=state.web_research_results[-1],
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
        message = f"Summarization error for topic '{state.research_topic}': {e}"
        logger.exception(
            "Summarization error",
            extra={
                "topic": state.research_topic,
                "has_context": bool(state.web_research_results),
                "error": str(e),
            },
        )
        return {
            "running_summary": state.running_summary or "Summary generation failed",
            "errors": [message],
        }
