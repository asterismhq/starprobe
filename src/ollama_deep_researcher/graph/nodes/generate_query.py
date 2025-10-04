from langchain_core.runnables import RunnableConfig

from ollama_deep_researcher.graph.state import SummaryState
from ollama_deep_researcher.services.llm_service import LLMService
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


def generate_query(state: SummaryState, config: RunnableConfig):
    """LangGraph node that generates a search query based on the research topic.

    Uses an LLM to create an optimized search query for web research based on
    the user's research topic. Uses Ollama as the LLM provider.

    Args:
        state: Current graph state containing the research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated query
    """
    configurable = OllamaDeepResearcherSettings.from_runnable_config(config)
    llm_client = config.get("llm_client")
    if not llm_client:
        raise ValueError("llm_client not provided in config")
    service = LLMService(configurable, llm_client)
    search_query = service.generate_search_query(state.research_topic)
    return {"search_query": search_query}
