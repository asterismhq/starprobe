from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from olm_d_rch.config.ollama_settings import OllamaSettings
from olm_d_rch.config.workflow_settings import WorkflowSettings
from olm_d_rch.container import DependencyContainer
from olm_d_rch.nodes import (
    finalize_summary,
    generate_query,
    reflect_on_summary,
    route_research,
    summarize_sources,
    web_research,
)
from olm_d_rch.state import (
    SummaryState,
    SummaryStateInput,
    SummaryStateOutput,
)


class ResearchGraph:
    def __init__(self, container: DependencyContainer):
        # Assign services from container
        self.container = container
        self.prompt_service = self.container.prompt_service
        self.research_service = self.container.research_service
        self.ollama_client = self.container.ollama_client

    def _configure_ollama_client(self, config: RunnableConfig):
        """Helper method to configure the Ollama client dynamically."""
        settings = OllamaSettings.from_runnable_config(config)
        self.ollama_client.configure(settings)

    async def generate_query(self, state: SummaryState, config: RunnableConfig):
        self._configure_ollama_client(config)
        return await generate_query(state, self.prompt_service, self.ollama_client)

    async def web_research(self, state: SummaryState, config: RunnableConfig):
        return await web_research(state, self.research_service)

    async def summarize_sources(self, state: SummaryState, config: RunnableConfig):
        self._configure_ollama_client(config)
        return await summarize_sources(state, self.prompt_service, self.ollama_client)

    async def reflect_on_summary(self, state: SummaryState, config: RunnableConfig):
        self._configure_ollama_client(config)
        return await reflect_on_summary(state, self.prompt_service, self.ollama_client)

    def route_research(self, state: SummaryState, config: RunnableConfig):
        return route_research(state, WorkflowSettings.from_runnable_config(config))

    def finalize_summary(self, state: SummaryState, config: RunnableConfig):
        return finalize_summary(state)

    def build(self):
        # Add nodes and edges
        builder = StateGraph(
            SummaryState,
            input_schema=SummaryStateInput,
            output_schema=SummaryStateOutput,
            context_schema=OllamaSettings,
        )

        builder.add_node("generate_query", self.generate_query)
        builder.add_node("web_research", self.web_research)
        builder.add_node("summarize_sources", self.summarize_sources)
        builder.add_node("reflect_on_summary", self.reflect_on_summary)
        builder.add_node("finalize_summary", self.finalize_summary)

        # Add edges
        builder.add_edge(START, "generate_query")
        builder.add_edge("generate_query", "web_research")
        builder.add_edge("web_research", "summarize_sources")
        builder.add_edge("summarize_sources", "reflect_on_summary")
        builder.add_conditional_edges("reflect_on_summary", self.route_research)
        builder.add_edge("finalize_summary", END)

        return builder.compile()


def build_graph():
    container = DependencyContainer()
    research_graph = ResearchGraph(container)
    return research_graph.build()
