import logging

from olm_d_rch.services.research_service import ResearchService


async def conduct_web_search(
    search_query: str,
    research_loop_count: int,
    web_research_results: list[str],
    sources_gathered: list[str],
    research_service: ResearchService,
):
    """LangGraph node that conducts web search using the generated search query.

    Executes a web search using the configured search API (tavily, perplexity,
    duckduckgo, or searxng) and formats the results for further processing.
    Uses ScrapingModel to fetch full page content from search result URLs.
    Includes comprehensive error handling to ensure graceful degradation.

    Args:
        search_query: The query to search for
        research_loop_count: Current loop count
        web_research_results: List of previous research results
        sources_gathered: List of previous sources
        research_service: Injected research service instance

    Returns:
        Dictionary with state update, including sources_gathered, research_loop_count, and web_research_results
    """
    logger = logging.getLogger(__name__)

    try:
        results, sources, errors = await research_service.search_and_scrape(
            query=search_query, loop_count=research_loop_count
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        diagnostic = f"Web research node failed: {exc}"
        logger.exception(diagnostic)
        return {
            "web_research_results": [],
            "sources_gathered": [],
            "research_loop_count": research_loop_count + 1,
            "errors": [diagnostic],
        }

    return {
        "web_research_results": [results],
        "sources_gathered": [sources],
        "research_loop_count": research_loop_count + 1,
        "errors": errors,
    }
