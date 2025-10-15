from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph

from olm_d_rch.nodes import (
    conduct_web_search,
    finalize_summary,
    refine_query,
    summarize_sources,
)
from olm_d_rch.protocols import LLMClientProtocol
from olm_d_rch.services import PromptService, ResearchService
from olm_d_rch.state import (
    SummaryState,
    SummaryStateInput,
    SummaryStateOutput,
)


class ResearchGraph:
    def __init__(
        self,
        prompt_service: PromptService,
        research_service: ResearchService,
        llm_client: LLMClientProtocol,
    ):
        # Assign services directly
        self.prompt_service = prompt_service
        self.research_service = research_service
        self.llm_client = llm_client

    async def refine_query(self, state: SummaryState, config: RunnableConfig):
        return await refine_query(
            state.research_topic, self.prompt_service, self.llm_client
        )

    async def conduct_web_search(self, state: SummaryState, config: RunnableConfig):
        return await conduct_web_search(
            state.search_query,
            state.research_loop_count,
            state.web_research_results,
            state.sources_gathered,
            self.research_service,
        )

    async def summarize_sources(self, state: SummaryState, config: RunnableConfig):
        return await summarize_sources(
            state.research_topic,
            state.running_summary,
            state.web_research_results,
            self.prompt_service,
            self.llm_client,
        )

    def finalize_summary(self, state: SummaryState, config: RunnableConfig):
        return finalize_summary(state)

    def build(self):
        # Add nodes and edges
        builder = StateGraph(
            SummaryState,
            input_schema=SummaryStateInput,
            output_schema=SummaryStateOutput,
        )

        builder.add_node("refine_query", self.refine_query)
        builder.add_node("conduct_web_search", self.conduct_web_search)
        builder.add_node("summarize_sources", self.summarize_sources)
        builder.add_node("finalize_summary", self.finalize_summary)

        # Add edges
        builder.add_edge(START, "refine_query")
        builder.add_edge("refine_query", "conduct_web_search")
        builder.add_edge("conduct_web_search", "summarize_sources")
        builder.add_edge("summarize_sources", "finalize_summary")

        return builder.compile()


def build_graph(
    prompt_service: PromptService,
    research_service: ResearchService,
    llm_client: LLMClientProtocol,
):
    research_graph = ResearchGraph(prompt_service, research_service, llm_client)
    return research_graph.build()
