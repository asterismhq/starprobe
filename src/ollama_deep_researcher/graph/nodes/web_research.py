from langchain_core.runnables import RunnableConfig

from ollama_deep_researcher.clients.duckduckgo_client import DuckDuckGoClient
from ollama_deep_researcher.graph.state import SummaryState
from ollama_deep_researcher.services.research_service import ResearchService
from ollama_deep_researcher.services.scraping_service import ScrapingService
from ollama_deep_researcher.services.search_service import SearchService
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


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
