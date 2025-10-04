from langchain_core.runnables import RunnableConfig
from typing_extensions import Literal

from ollama_deep_researcher.graph.state import SummaryState
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


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
