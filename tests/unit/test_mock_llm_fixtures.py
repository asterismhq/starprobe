"""Unit tests for LLM mock fixtures and node integration."""

import json

import pytest

from src.starprobe.config.workflow_settings import WorkflowSettings
from src.starprobe.nodes.node1_refine_query import refine_query
from src.starprobe.nodes.node3_summarize_sources import summarize_sources
from src.starprobe.services.prompt_service import PromptService
from src.starprobe.services.text_processing_service import TextProcessingService


class TestLLMMockFixtures:
    """Test that LLM mock fixtures work correctly with nodes."""

    @pytest.mark.asyncio
    async def test_mock_llm_json_returns_json_string(self, mock_llm_json):
        """Test that mock_llm_json fixture returns a client with JSON string content."""
        result = await mock_llm_json.invoke([{"role": "user", "content": "test"}])
        assert isinstance(result.content, str)
        parsed = json.loads(result.content)
        assert "query" in parsed
        assert "rationale" in parsed

    @pytest.mark.asyncio
    async def test_mock_llm_tool_returns_tool_calls(self, mock_llm_tool):
        """Test that mock_llm_tool fixture returns a client with tool calls."""
        result = await mock_llm_tool.invoke([{"role": "user", "content": "test"}])
        assert result.tool_calls
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0]["name"] == "Query"
        assert "query" in result.tool_calls[0]["args"]

    @pytest.mark.asyncio
    async def test_mock_llm_summary_returns_summary_content(self, mock_llm_summary):
        """Test that mock_llm_summary fixture returns a client with summary content."""
        result = await mock_llm_summary.invoke([{"role": "user", "content": "test"}])
        assert isinstance(result.content, str)
        assert "summary" in result.content.lower()


class TestNodeIntegration:
    """Test nodes with mock LLM fixtures."""

    @pytest.fixture
    def prompt_service(self):
        """Create a prompt service for testing."""
        settings = WorkflowSettings()
        return PromptService(settings)

    @pytest.fixture
    def text_processing_service(self):
        """Create a text processing service for testing."""
        return TextProcessingService

    @pytest.mark.asyncio
    async def test_refine_query_tool_calling_with_mock_llm(
        self, mock_llm_tool, prompt_service
    ):
        """Test refine_query node with tool-calling mock LLM."""
        # Configure prompt service to use tool calling
        prompt_service.configurable.use_tool_calling = True

        result = await refine_query(
            research_topic="test topic",
            prompt_service=prompt_service,
            llm_client=mock_llm_tool,
        )

        assert "search_query" in result
        assert result["search_query"] == "test query"

    @pytest.mark.asyncio
    async def test_refine_query_json_mode_with_mock_llm(
        self, mock_llm_json, prompt_service
    ):
        """Test refine_query node with JSON-mode mock LLM."""
        # Configure prompt service to use JSON mode
        prompt_service.configurable.use_tool_calling = False

        result = await refine_query(
            research_topic="test topic",
            prompt_service=prompt_service,
            llm_client=mock_llm_json,
        )

        assert "search_query" in result
        assert result["search_query"] == "test query"

    @pytest.mark.asyncio
    async def test_summarize_sources_with_mock_llm(
        self, mock_llm_summary, prompt_service, text_processing_service
    ):
        """Test summarize_sources node with mock LLM."""
        web_results = ["Result 1 content", "Result 2 content"]

        result = await summarize_sources(
            research_topic="test topic",
            running_summary="Previous summary",
            web_research_results=web_results,
            prompt_service=prompt_service,
            llm_client=mock_llm_summary,
        )

        assert "running_summary" in result
        assert "test summary" in result["running_summary"]
