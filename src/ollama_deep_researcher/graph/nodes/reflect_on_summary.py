from langchain_core.runnables import RunnableConfig

from ollama_deep_researcher.graph.state import SummaryState
from ollama_deep_researcher.services.llm_service import LLMService
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


def reflect_on_summary(state: SummaryState, config: RunnableConfig):
    """LangGraph node that identifies knowledge gaps and generates follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    a new search query to address those gaps. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        config: OllamaDeepResearcherSettings for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
    """
    configurable = OllamaDeepResearcherSettings.from_runnable_config(config)
    llm_client = config.get("llm_client")
    if not llm_client:
        raise ValueError("llm_client not provided in config")
    service = LLMService(configurable, llm_client)
    search_query = service.reflect_and_generate_follow_up_query(
        research_topic=state.research_topic, running_summary=state.running_summary
    )
    return {"search_query": search_query}
