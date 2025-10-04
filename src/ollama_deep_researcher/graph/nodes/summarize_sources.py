from langchain_core.runnables import RunnableConfig

from ollama_deep_researcher.graph.state import SummaryState
from ollama_deep_researcher.services.llm_service import LLMService
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


def summarize_sources(state: SummaryState, config: RunnableConfig):
    """LangGraph node that summarizes web research results.

    Uses an LLM to create or update a running summary based on the newest web research
    results, integrating them with any existing summary.
    Includes error handling to ensure graceful degradation.

    Args:
        state: Current graph state containing research topic, running summary,
              and web research results
        config: OllamaDeepResearcherSettings for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including running_summary key containing the updated summary
    """
    try:
        configurable = OllamaDeepResearcherSettings.from_runnable_config(config)
        llm_client = config.get("llm_client")
        if not llm_client:
            raise ValueError("llm_client not provided in config")
        service = LLMService(configurable, llm_client)
        running_summary = service.summarize(
            research_topic=state.research_topic,
            existing_summary=state.running_summary,
            new_context=state.web_research_results[-1],
        )
        return {"running_summary": running_summary}
    except Exception as e:
        # Log error but preserve existing summary or return fallback
        print(f"Summarization error: {str(e)}")
        return {"running_summary": state.running_summary or "Summary generation failed"}
