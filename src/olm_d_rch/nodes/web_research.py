import logging

from olm_d_rch.services.research_service import ResearchService
from olm_d_rch.state import SummaryState


async def web_research(state: SummaryState, research_service: ResearchService):
    """LangGraph node that performs web research using the generated search query.

    Executes a web search using the configured search API (tavily, perplexity,
    duckduckgo, or searxng) and formats the results for further processing.
    Uses ScrapingModel to fetch full page content from search result URLs.
    Includes comprehensive error handling to ensure graceful degradation.

    Args:
        state: Current graph state containing the search query and research loop count
        research_service: Injected research service instance

    Returns:
        Dictionary with state update, including sources_gathered, research_loop_count, and web_research_results
    """
    logger = logging.getLogger(__name__)

    try:
        results, sources, errors = await research_service.search_and_scrape(
            query=state.search_query, loop_count=state.research_loop_count
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        diagnostic = f"Web research node failed: {exc}"
        logger.exception(diagnostic)
        return {
            "web_research_results": state.web_research_results,
            "sources_gathered": state.sources_gathered,
            "research_loop_count": state.research_loop_count + 1,
            "errors": [diagnostic],
        }

    return {
        "web_research_results": state.web_research_results + [results],
        "sources_gathered": state.sources_gathered + [sources],
        "research_loop_count": state.research_loop_count + 1,
        "errors": errors,
    }
