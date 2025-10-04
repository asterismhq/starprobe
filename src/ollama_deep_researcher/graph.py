from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from typing_extensions import Literal

from ollama_deep_researcher.clients.duckduckgo_client import DuckDuckGoClient
from ollama_deep_researcher.services import LLMService, ResearchService, SearchService, ScrapingService
from ollama_deep_researcher.settings import (
    OllamaClient,
    OllamaDeepResearcherSettings,
)
from ollama_deep_researcher.state import (
    SummaryState,
    SummaryStateInput,
    SummaryStateOutput,
)

# Constants
MAX_TOKENS_PER_SOURCE = 1000


def get_llm(config: OllamaDeepResearcherSettings):
    """Get an LLM client based on the configuration."""
    if config.use_tool_calling:
        return OllamaClient(
            config,
            base_url=config.ollama_base_url,
            model=config.local_llm,
            temperature=0,
        )
    else:
        return OllamaClient(
            config,
            base_url=config.ollama_base_url,
            model=config.local_llm,
            temperature=0,
            format="json",
        )


# Nodes
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
    service = LLMService(configurable)
    search_query = service.generate_search_query(state.research_topic)
    return {"search_query": search_query}


def web_research(state: SummaryState, config: RunnableConfig):
    """LangGraph node that performs web research using the generated search query.

    Executes a web search using the configured search API (tavily, perplexity,
    duckduckgo, or searxng) and formats the results for further processing.
    Uses ScrapingModel to fetch full page content from search result URLs.
    Includes comprehensive error handling to ensure graceful degradation.

    Args:
        state: Current graph state containing the search query and research loop count
        config: OllamaDeepResearcherSettings for the runnable, including search API settings

    Returns:
        Dictionary with state update, including sources_gathered, research_loop_count, and web_research_results
    """
    configurable = OllamaDeepResearcherSettings.from_runnable_config(config)
    search_client = DuckDuckGoClient()
    search_service = SearchService(search_client)
    scraper = ScrapingService()
    service = ResearchService(configurable, search_service, scraper)
    results, sources = service.search_and_scrape(
        query=state.search_query, loop_count=state.research_loop_count
    )
    return {
        "web_research_results": state.web_research_results + [results],
        "sources_gathered": state.sources_gathered + [sources],
        "research_loop_count": state.research_loop_count + 1,
    }


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
        service = LLMService(configurable)
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
    service = LLMService(configurable)
    search_query = service.reflect_and_generate_follow_up_query(
        research_topic=state.research_topic, running_summary=state.running_summary
    )
    return {"search_query": search_query}


def finalize_summary(state: SummaryState):
    """LangGraph node that finalizes the research summary.

    Prepares the final output by deduplicating and formatting sources, then
    combining them with the running summary to create a well-structured
    research report with proper citations.
    Populates success/error metadata for API response.

    Args:
        state: Current graph state containing the running summary and sources gathered

    Returns:
        Dictionary with state update, including running_summary, success, sources, and error_message
    """

    # Deduplicate sources before joining
    seen_sources = set()
    unique_sources = []

    for source in state.sources_gathered:
        # Split the source into lines and process each individually
        for line in source.split("\n"):
            # Only process non-empty lines
            if line.strip() and line not in seen_sources:
                seen_sources.add(line)
                unique_sources.append(line)

    # Extract source URLs
    source_urls = []
    for line in unique_sources:
        # Look for lines that start with http
        if line.strip().startswith("http"):
            source_urls.append(line.strip())

    # Determine success based on content quality
    has_summary = bool(state.running_summary and len(state.running_summary) > 50)
    has_sources = len(source_urls) > 0
    success = has_summary and has_sources

    # Set error message if not successful
    error_message = None
    if not success:
        if not has_summary:
            error_message = "Failed to generate summary"
        elif not has_sources:
            error_message = "No sources found"

    # Join the deduplicated sources
    all_sources = "\n".join(unique_sources)
    formatted_summary = (
        f"## Summary\n{state.running_summary}\n\n ### Sources:\n{all_sources}"
    )

    return {
        "running_summary": formatted_summary,
        "success": success,
        "sources": source_urls,
        "error_message": error_message,
    }


def route_research(
    state: SummaryState, config: RunnableConfig
) -> Literal["finalize_summary", "web_research"]:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        config: OllamaDeepResearcherSettings for the runnable, including max_web_research_loops setting

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
    """

    configurable = OllamaDeepResearcherSettings.from_runnable_config(config)
    if state.research_loop_count <= configurable.max_web_research_loops:
        return "web_research"
    else:
        return "finalize_summary"


# Add nodes and edges
builder = StateGraph(
    SummaryState,
    input=SummaryStateInput,
    output=SummaryStateOutput,
    config_schema=OllamaDeepResearcherSettings,
)
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("summarize_sources", summarize_sources)
builder.add_node("reflect_on_summary", reflect_on_summary)
builder.add_node("finalize_summary", finalize_summary)

# Add edges
builder.add_edge(START, "generate_query")
builder.add_edge("generate_query", "web_research")
builder.add_edge("web_research", "summarize_sources")
builder.add_edge("summarize_sources", "reflect_on_summary")
builder.add_conditional_edges("reflect_on_summary", route_research)
builder.add_edge("finalize_summary", END)

graph = builder.compile()
