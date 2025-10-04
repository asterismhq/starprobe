import json
import jinja2
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from ollama_deep_researcher.prompts.components import (
    json_mode_query_instructions,
    json_mode_reflection_instructions,
    query_writer_instructions,
    reflection_instructions,
    summarizer_instructions,
    tool_calling_query_instructions,
    tool_calling_reflection_instructions,
)
from ollama_deep_researcher.clients.ollama_client import OllamaClient
from ollama_deep_researcher.settings import (
    OllamaDeepResearcherSettings,
)
from ollama_deep_researcher.services.text_processing_service import TextProcessingService


class LLMService:
    """Service class for handling LLM interactions.

    Dependencies:
    - TextProcessingService: For stripping thinking tokens and text processing
    - OllamaDeepResearcherSettings: For configuration and LLM client setup
    - ollama_deep_researcher.prompts: For query generation and summarization prompts
    """

    @staticmethod
    def get_current_date():
        """Get current date in a readable format."""
        return datetime.now().strftime("%B %d, %Y")

    def __init__(self, configurable: OllamaDeepResearcherSettings):
        self.configurable = configurable
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('src/ollama_deep_researcher/prompts/templates')
        )

    def generate_search_query(self, research_topic: str) -> str:
        """Generate a search query based on the research topic."""
        # Render the prompt using Jinja template
        template = self.template_env.get_template('query.jinja')
        formatted_prompt = template.render(
            query_writer_instructions=query_writer_instructions,
            tool_calling_query_instructions=tool_calling_query_instructions,
            json_mode_query_instructions=json_mode_query_instructions,
            use_tool_calling=self.configurable.use_tool_calling,
            current_date=self.get_current_date(),
            research_topic=research_topic
        )

        @tool
        class Query(BaseModel):
            """
            This tool is used to generate a query for web search.
            """

            query: str = Field(description="The actual search query string")
            rationale: str = Field(
                description="Brief explanation of why this query is relevant"
            )

        messages = [
            SystemMessage(content=formatted_prompt),
            HumanMessage(content="Generate a query for web search:"),
        ]

        return self._generate_search_query_with_structured_output(
            messages=messages,
            tool_class=Query,
            fallback_query=f"Tell me more about {research_topic}",
            tool_query_field="query",
            json_query_field="query",
        )

    def summarize(
        self, research_topic: str, existing_summary: str, new_context: str
    ) -> str:
        """Summarize web research results."""
        # Build the human message
        if existing_summary:
            human_message_content = (
                f"<Existing Summary> \n {existing_summary} \n <Existing Summary>\n\n"
                f"<New Context> \n {new_context} \n <New Context>"
                f"Update the Existing Summary with the New Context on this topic: \n <User Input> \n {research_topic} \n <User Input>\n\n"
            )
        else:
            human_message_content = (
                f"<Context> \n {new_context} \n <Context>"
                f"Create a Summary using the Context on this topic: \n <User Input> \n {research_topic} \n <User Input>\n\n"
            )

        # Render the prompt using Jinja template
        template = self.template_env.get_template('summarize.jinja')
        prompt = template.render(summarizer_instructions=summarizer_instructions)

        # Run the LLM
        llm = OllamaClient(
            self.configurable,
            base_url=self.configurable.ollama_base_url,
            model=self.configurable.local_llm,
            temperature=0,
        )

        result = llm.invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(content=human_message_content),
            ]
        )

        # Strip thinking tokens if configured
        running_summary = result.content
        if self.configurable.strip_thinking_tokens:
            running_summary = TextProcessingService.strip_thinking_tokens(running_summary)

        return running_summary

    def reflect_and_generate_follow_up_query(
        self, research_topic: str, running_summary: str
    ) -> str:
        """Identify knowledge gaps and generate follow-up queries."""
        # Render the prompt using Jinja template
        template = self.template_env.get_template('reflect.jinja')
        formatted_prompt = template.render(
            reflection_instructions=reflection_instructions,
            tool_calling_reflection_instructions=tool_calling_reflection_instructions,
            json_mode_reflection_instructions=json_mode_reflection_instructions,
            use_tool_calling=self.configurable.use_tool_calling,
            research_topic=research_topic
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

        messages = [
            SystemMessage(content=formatted_prompt),
            HumanMessage(
                content=f"Reflect on our existing knowledge: \n === \n {running_summary}, \n === \n And now identify a knowledge gap and generate a follow-up web search query:"
            ),
        ]

        return self._generate_search_query_with_structured_output(
            messages=messages,
            tool_class=FollowUpQuery,
            fallback_query=f"Tell me more about {research_topic}",
            tool_query_field="follow_up_query",
            json_query_field="follow_up_query",
        )

    def _generate_search_query_with_structured_output(
        self,
        messages: list,
        tool_class,
        fallback_query: str,
        tool_query_field: str,
        json_query_field: str,
    ):
        """Helper function to generate search queries using either tool calling or JSON mode."""
        if self.configurable.use_tool_calling:
            llm = self._get_llm().bind_tools([tool_class])
            result = llm.invoke(messages)

            if not result.tool_calls:
                return fallback_query

            try:
                tool_data = result.tool_calls[0]["args"]
                search_query = tool_data.get(tool_query_field)
                return search_query
            except (IndexError, KeyError):
                return fallback_query

        else:
            # Use JSON mode
            llm = self._get_llm()
            result = llm.invoke(messages)
            print(f"result: {result}")
            content = result.content

            try:
                parsed_json = json.loads(content)
                search_query = parsed_json.get(json_query_field)
                if not search_query:
                    return fallback_query
                return search_query
            except (json.JSONDecodeError, KeyError):
                if self.configurable.strip_thinking_tokens:
                    content = TextProcessingService.strip_thinking_tokens(content)
                return fallback_query

    def _get_llm(self):
        """Initialize Ollama LLM client based on configuration."""
        if self.configurable.use_tool_calling:
            return OllamaClient(
                self.configurable,
                base_url=self.configurable.ollama_base_url,
                model=self.configurable.local_llm,
                temperature=0,
            )
        else:
            return OllamaClient(
                self.configurable,
                base_url=self.configurable.ollama_base_url,
                model=self.configurable.local_llm,
                temperature=0,
                format="json",
            )
