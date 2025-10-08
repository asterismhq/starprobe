from ollama_deep_researcher.protocols.ollama_client_protocol import OllamaClientProtocol
from ollama_deep_researcher.services.prompt_service import PromptService
from ollama_deep_researcher.services.text_processing_service import (
    TextProcessingService,
)
from ollama_deep_researcher.state import SummaryState


async def summarize_sources(
    state: SummaryState,
    prompt_service: PromptService,
    ollama_client: OllamaClientProtocol,
):
    """LangGraph node that summarizes web research results.

    Uses an LLM to create or update a running summary based on the newest web research
    results, integrating them with any existing summary.
    Includes error handling to ensure graceful degradation.

    Args:
        state: Current graph state containing research topic, running summary,
              and web research results
        prompt_service: Service for generating prompts
        ollama_client: Client for LLM interactions

    Returns:
        Dictionary with state update, including running_summary key containing the updated summary
    """
    try:
        messages = prompt_service.generate_summarize_prompt(
            research_topic=state.research_topic,
            existing_summary=state.running_summary,
            new_context=state.web_research_results[-1],
        )
        result = await ollama_client.invoke(messages)

        # Strip thinking tokens if configured
        running_summary = result.content
        if prompt_service.configurable.strip_thinking_tokens:
            running_summary = TextProcessingService.strip_thinking_tokens(
                running_summary
            )

        return {"running_summary": running_summary}
    except Exception as e:
        # Log error but preserve existing summary or return fallback
        print(f"Summarization error: {str(e)}")
        return {"running_summary": state.running_summary or "Summary generation failed"}
