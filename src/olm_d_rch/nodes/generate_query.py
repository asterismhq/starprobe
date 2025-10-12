import json
import logging

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from olm_d_rch.protocols.llm_client_protocol import LLMClientProtocol
from olm_d_rch.services.prompt_service import PromptService
from olm_d_rch.state import SummaryState


async def generate_query(
    state: SummaryState,
    prompt_service: PromptService,
    llm_client: LLMClientProtocol,
):
    """LangGraph node that generates a search query based on the research topic.

    Uses an LLM to create an optimized search query for web research based on
    the user's research topic via the configured backend (e.g., Ollama, MLX).

    Args:
        state: Current graph state containing the research topic
        prompt_service: Service for generating prompts
        llm_client: Client for LLM interactions

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

    logger = logging.getLogger(__name__)

    error_messages: list[str] | None = None

    try:
        if prompt_service.configurable.use_tool_calling:
            llm = llm_client.bind_tools([Query])
            result = await llm.invoke(messages)

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
            result = await llm_client.invoke(messages)
            content = result.content

            try:
                parsed_json = json.loads(content)
                search_query = parsed_json.get("query")
                if not search_query:
                    search_query = fallback_query
            except (json.JSONDecodeError, KeyError):
                search_query = fallback_query
    except Exception as exc:  # pragma: no cover - defensive guard
        search_query = fallback_query
        error_messages = [f"Generate query fallback triggered: {exc}"]
        logger.exception(
            "Failed to generate search query",
            extra={"topic": state.research_topic, "error": str(exc)},
        )

    response = {"search_query": search_query}
    if error_messages is not None:
        response["errors"] = error_messages
    return response
