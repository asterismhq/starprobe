import operator
from dataclasses import dataclass, field

from typing_extensions import Annotated


@dataclass(kw_only=True)
class SummaryState:
    research_topic: str = field(default=None)
    search_query: str = field(default=None)
    web_research_results: Annotated[list, operator.add] = field(default_factory=list)
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list)
    research_loop_count: int = field(default=0)
    running_summary: str = field(default=None)
    errors: Annotated[list[str], operator.add] = field(default_factory=list)
    warnings: Annotated[list[str], operator.add] = field(default_factory=list)


@dataclass(kw_only=True)
class SummaryStateInput:
    research_topic: str = field(default=None)


@dataclass(kw_only=True)
class SummaryStateOutput:
    success: bool = field(default=False)
    running_summary: str = field(default=None)
    sources: list[str] = field(default_factory=list)
    error_message: str = field(default=None)
    diagnostics: list[str] = field(default_factory=list)
