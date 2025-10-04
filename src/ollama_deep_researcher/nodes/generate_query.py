import json

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from ollama_deep_researcher.protocols.ollama_client_protocol import OllamaClientProtocol
from ollama_deep_researcher.services.prompt_service import PromptService
from ollama_deep_researcher.state import SummaryState


def generate_query(
    state: SummaryState,
    prompt_service: PromptService,
    ollama_client: OllamaClientProtocol,
):
    """LangGraph node that generates a search query based on the research topic.

    Uses an LLM to create an optimized search query for web research based on
    the user's research topic. Uses Ollama as the LLM provider.

    Args:
        state: Current graph state containing the research topic
        prompt_service: Service for generating prompts
        ollama_client: Client for LLM interactions

    Returns:
        Dictionary with state update, including search_query key containing the generated query
    """
    messages = prompt_service.generate_query_prompt(state.research_topic)

    @tool
    class Query(BaseModel):
        """
        This tool is used to generate a query for web search.
        """

        query: str = Field(description="The actual search query string")
        rationale: str = Field(
            description="Brief explanation of why this query is relevant"
        )

    fallback_query = f"Tell me more about {state.research_topic}"

    if prompt_service.configurable.use_tool_calling:
        llm = ollama_client.bind_tools([Query])
        result = llm.invoke(messages)

        if not result.tool_calls:
            search_query = fallback_query
        else:
            try:
                tool_data = result.tool_calls[0]["args"]
                search_query = tool_data.get("query", fallback_query)
            except (IndexError, KeyError):
                search_query = fallback_query
    else:
        # Use JSON mode
        result = ollama_client.invoke(messages)
        content = result.content

        try:
            parsed_json = json.loads(content)
            search_query = parsed_json.get("query")
            if not search_query:
                search_query = fallback_query
        except (json.JSONDecodeError, KeyError):
            search_query = fallback_query

    return {"search_query": search_query}
