import json

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from ollama_deep_researcher.protocols.ollama_client_protocol import OllamaClientProtocol
from ollama_deep_researcher.services.prompt_service import PromptService
from ollama_deep_researcher.state import SummaryState


async def reflect_on_summary(
    state: SummaryState,
    prompt_service: PromptService,
    ollama_client: OllamaClientProtocol,
):
    """LangGraph node that identifies knowledge gaps and generates follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    a new search query to address those gaps. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        prompt_service: Service for generating prompts
        ollama_client: Client for LLM interactions

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
    """
    messages = prompt_service.generate_reflect_prompt(
        research_topic=state.research_topic, running_summary=state.running_summary
    )

    @tool
    class FollowUpQuery(BaseModel):
        """
        This tool is used to generate a follow-up query to address a knowledge gap.
        """

        follow_up_query: str = Field(
            description="Write a specific question to address this gap"
        )
        knowledge_gap: str = Field(
            description="Describe what information is missing or needs clarification"
        )

    fallback_query = f"Tell me more about {state.research_topic}"

    if prompt_service.configurable.use_tool_calling:
        llm = ollama_client.bind_tools([FollowUpQuery])
        result = await llm.invoke(messages)

        if not result.tool_calls:
            search_query = fallback_query
        else:
            try:
                tool_data = result.tool_calls[0]["args"]
                search_query = tool_data.get("follow_up_query", fallback_query)
            except (IndexError, KeyError):
                search_query = fallback_query
    else:
        # Use JSON mode
        result = await ollama_client.invoke(messages)
        content = result.content

        try:
            parsed_json = json.loads(content)
            search_query = parsed_json.get("follow_up_query")
            if not search_query:
                search_query = fallback_query
        except (json.JSONDecodeError, KeyError):
            search_query = fallback_query

    return {"search_query": search_query}
