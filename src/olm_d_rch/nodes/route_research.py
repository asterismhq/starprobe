from typing_extensions import Literal

from olm_d_rch.config.workflow_settings import WorkflowSettings
from olm_d_rch.state import SummaryState


def route_research(
    state: SummaryState, settings: WorkflowSettings
) -> Literal["finalize_summary", "web_research"]:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        settings: WorkflowSettings for the runnable, including max_web_research_loops setting

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
    """

    if state.research_loop_count <= settings.max_web_research_loops:
        return "web_research"
    else:
        return "finalize_summary"
