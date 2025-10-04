from functools import partial
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from ollama_deep_researcher.clients.duckduckgo_client import DuckDuckGoClient
from ollama_deep_researcher.clients.ollama_client import OllamaClient
from ollama_deep_researcher.services.prompt_service import PromptService
from ollama_deep_researcher.services.research_service import ResearchService
from ollama_deep_researcher.services.scraping_service import ScrapingService
from ollama_deep_researcher.services.search_service import SearchService
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings
from ollama_deep_researcher.state import (
    SummaryState,
    SummaryStateInput,
    SummaryStateOutput,
)
from ollama_deep_researcher.nodes import (
    finalize_summary,
    generate_query,
    reflect_on_summary,
    route_research,
    summarize_sources,
    web_research,
)

# Constants
MAX_TOKENS_PER_SOURCE = 1000


class ResearchGraph:
    def __init__(self):
        # Instantiate all clients and services here
        self.settings = OllamaDeepResearcherSettings()
        self.ollama_client = OllamaClient(self.settings)
        self.duckduckgo_client = DuckDuckGoClient()
        self.prompt_service = PromptService(self.settings)
        self.search_service = SearchService(self.duckduckgo_client)
        self.scraping_service = ScrapingService()
        self.research_service = ResearchService(self.settings, self.search_service, self.scraping_service)

    def generate_query(self, state: SummaryState, config: RunnableConfig):
        # Configure the client dynamically
        configurable = config.get("configurable", {})
        model = configurable.get("local_llm")
        base_url = configurable.get("ollama_base_url")
        if model or base_url:
            self.ollama_client.configure(model=model, base_url=base_url)
        return generate_query(state, self.prompt_service, self.ollama_client)

    def web_research(self, state: SummaryState, config: RunnableConfig):
        return web_research(state, self.research_service)

    def summarize_sources(self, state: SummaryState, config: RunnableConfig):
        # Configure the client dynamically
        configurable = config.get("configurable", {})
        model = configurable.get("local_llm")
        base_url = configurable.get("ollama_base_url")
        if model or base_url:
            self.ollama_client.configure(model=model, base_url=base_url)
        return summarize_sources(state, self.prompt_service, self.ollama_client)

    def reflect_on_summary(self, state: SummaryState, config: RunnableConfig):
        # Configure the client dynamically
        configurable = config.get("configurable", {})
        model = configurable.get("local_llm")
        base_url = configurable.get("ollama_base_url")
        if model or base_url:
            self.ollama_client.configure(model=model, base_url=base_url)
        return reflect_on_summary(state, self.prompt_service, self.ollama_client)

    def route_research(self, state: SummaryState, config: RunnableConfig):
        settings = OllamaDeepResearcherSettings.from_runnable_config(config)
        return route_research(state, settings)

    def finalize_summary(self, state: SummaryState, config: RunnableConfig):
        return finalize_summary(state)

    def build(self):
        # Add nodes and edges
        builder = StateGraph(
            SummaryState,
            input=SummaryStateInput,
            output=SummaryStateOutput,
            config_schema=OllamaDeepResearcherSettings,
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
    research_graph = ResearchGraph()
    return research_graph.build()
