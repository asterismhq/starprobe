import json
from datetime import datetime

import jinja2
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
from ollama_deep_researcher.settings import (
    OllamaDeepResearcherSettings,
)


class PromptService:
    """Service class for generating LLM prompts.

    Dependencies:
    - OllamaDeepResearcherSettings: For configuration
    - ollama_deep_researcher.prompts: For prompt templates and instructions
    """

    @staticmethod
    def get_current_date():
        """Get current date in a readable format."""
        return datetime.now().strftime("%B %d, %Y")

    def __init__(self, configurable: OllamaDeepResearcherSettings):
        self.configurable = configurable
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                "src/ollama_deep_researcher/prompts/templates"
            )
        )

    def generate_query_prompt(self, research_topic: str) -> list:
        """Generate messages for search query generation."""
        # Render the prompt using Jinja template
        template = self.template_env.get_template("query.jinja")
        formatted_prompt = template.render(
            query_writer_instructions=query_writer_instructions,
            tool_calling_query_instructions=tool_calling_query_instructions,
            json_mode_query_instructions=json_mode_query_instructions,
            use_tool_calling=self.configurable.use_tool_calling,
            current_date=self.get_current_date(),
            research_topic=research_topic,
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

        return messages

    def generate_summarize_prompt(
        self, research_topic: str, existing_summary: str, new_context: str
    ) -> list:
        """Generate messages for summarization."""
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
        template = self.template_env.get_template("summarize.jinja")
        prompt = template.render(summarizer_instructions=summarizer_instructions)

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=human_message_content),
        ]

        return messages

    def generate_reflect_prompt(self, research_topic: str, running_summary: str) -> list:
        """Generate messages for reflection and follow-up query generation."""
        # Render the prompt using Jinja template
        template = self.template_env.get_template("reflect.jinja")
        formatted_prompt = template.render(
            reflection_instructions=reflection_instructions,
            tool_calling_reflection_instructions=tool_calling_reflection_instructions,
            json_mode_reflection_instructions=json_mode_reflection_instructions,
            use_tool_calling=self.configurable.use_tool_calling,
            research_topic=research_topic,
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

        return messages


