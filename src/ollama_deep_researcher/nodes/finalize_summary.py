import logging

from ollama_deep_researcher.state import SummaryState


logger = logging.getLogger(__name__)


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
    has_errors = bool(state.errors)
    success = has_summary and has_sources and not has_errors

    # Set error message if not successful
    error_message = None
    if not success:
        if not has_summary:
            error_message = "Failed to generate summary"
        elif not has_sources:
            error_message = "No sources found"
        elif has_errors:
            error_message = "Diagnostics reported during research"

    diagnostics = state.errors
    if not success and diagnostics:
        joined = "; ".join(dict.fromkeys(diagnostics))
        error_message = f"{error_message}. Diagnostics: {joined}" if error_message else joined
        logger.error("Finalize summary detected errors", extra={"diagnostics": joined})

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
        "diagnostics": diagnostics,
    }
