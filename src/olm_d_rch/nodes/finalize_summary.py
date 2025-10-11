import logging

from olm_d_rch.state import SummaryState

logger = logging.getLogger(__name__)


def finalize_summary(state: SummaryState):
    """LangGraph node that finalizes the research summary.

    Builds a Markdown article from accumulated state values and prepares
    metadata for API consumers.
    """

    # Deduplicate sources while preserving order
    seen_sources = set()
    unique_sources: list[str] = []

    for source in state.sources_gathered:
        for line in source.split("\n"):
            cleaned = line.strip()
            if cleaned and cleaned not in seen_sources:
                seen_sources.add(cleaned)
                unique_sources.append(cleaned)

    source_urls = [line for line in unique_sources if line.startswith("http")]

    article_sections: list[str] = []
    title = state.research_topic or "Research Article"
    article_sections.append(f"# {title}")

    summary_body = state.running_summary or "Summary generation unavailable."
    article_sections.append("")
    article_sections.append("## Summary")
    article_sections.append("")
    article_sections.append(summary_body)

    if source_urls:
        article_sections.append("")
        article_sections.append("## Sources")
        article_sections.append("")
        for index, url in enumerate(source_urls, start=1):
            article_sections.append(f"{index}. {url}")

    article = "\n".join(article_sections).strip()

    has_summary = bool(summary_body and len(summary_body) > 50)
    has_sources = len(source_urls) > 0
    has_errors = bool(state.errors)
    success = has_summary and has_sources and not has_errors

    error_message = None
    if not success:
        if not has_summary:
            error_message = "Failed to generate summary"
        elif not has_sources:
            error_message = "No sources found"
        elif has_errors:
            error_message = "Errors occurred during research"

    diagnostics = list(dict.fromkeys(state.errors))
    if state.errors:
        joined = "; ".join(diagnostics)
        if not error_message:
            error_message = joined
        else:
            error_message = f"{error_message}. Details: {joined}"
        logger.error("Research completed with errors", extra={"errors": joined})

    metadata = {
        "sources": source_urls,
        "source_count": len(source_urls),
    }

    return {
        "article": article,
        "success": success,
        "metadata": metadata,
        "error_message": error_message,
        "diagnostics": diagnostics,
    }
