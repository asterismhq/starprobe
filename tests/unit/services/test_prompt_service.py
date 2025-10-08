"""Unit tests for PromptService."""

import pytest
from langchain_core.messages import HumanMessage, SystemMessage

from ollama_deep_researcher.services.prompt_service import PromptService


class TestPromptService:
    """Test cases for PromptService."""

    @pytest.fixture
    def prompt_service(self, default_settings):
        """Create a PromptService instance for testing."""
        return PromptService(default_settings)

    def test_get_current_date(self, mocker):
        """Test current date formatting."""
        from datetime import datetime

        # Mock datetime.now() to return a fixed date
        mock_datetime = mocker.patch(
            "ollama_deep_researcher.services.prompt_service.datetime"
        )
        mock_now = datetime(2024, 7, 26)
        mock_datetime.now.return_value = mock_now

        result = PromptService.get_current_date()
        assert result == "July 26, 2024"

    def test_generate_query_prompt_returns_messages(self, prompt_service):
        """Test query prompt generation returns list of messages."""
        result = prompt_service.generate_query_prompt("AI research")
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], SystemMessage)
        assert isinstance(result[1], HumanMessage)

    def test_generate_query_prompt_contains_topic(self, prompt_service):
        """Test query prompt includes the research topic."""
        topic = "quantum computing"
        result = prompt_service.generate_query_prompt(topic)
        # Check that topic appears in the system message
        assert topic in result[0].content

    def test_generate_query_prompt_includes_current_date(self, prompt_service):
        """Test query prompt includes current date."""
        result = prompt_service.generate_query_prompt("test topic")
        current_date = PromptService.get_current_date()
        assert current_date in result[0].content

    def test_generate_summarize_prompt_initial(self, prompt_service):
        """Test summarize prompt for initial summary (no existing summary)."""
        topic = "machine learning"
        new_context = "New research findings about ML"
        result = prompt_service.generate_summarize_prompt(topic, "", new_context)

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], SystemMessage)
        assert isinstance(result[1], HumanMessage)

        # Should contain the new context and topic
        assert new_context in result[1].content
        assert topic in result[1].content
        # Should say "Create a Summary" for initial summary
        assert "Create a Summary" in result[1].content

    def test_generate_summarize_prompt_update(self, prompt_service):
        """Test summarize prompt for updating existing summary."""
        topic = "machine learning"
        existing_summary = "ML is a subset of AI"
        new_context = "Deep learning is a subset of ML"
        result = prompt_service.generate_summarize_prompt(
            topic, existing_summary, new_context
        )

        assert isinstance(result, list)
        assert len(result) == 2

        # Should contain both existing summary and new context
        assert existing_summary in result[1].content
        assert new_context in result[1].content
        assert topic in result[1].content
        # Should say "Update the Existing Summary" for updates
        assert "Update the Existing Summary" in result[1].content

    def test_generate_reflect_prompt_returns_messages(self, prompt_service):
        """Test reflect prompt generation returns list of messages."""
        topic = "AI safety"
        summary = "Current understanding of AI alignment"
        result = prompt_service.generate_reflect_prompt(topic, summary)

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], SystemMessage)
        assert isinstance(result[1], HumanMessage)

    def test_generate_reflect_prompt_contains_topic_and_summary(self, prompt_service):
        """Test reflect prompt includes topic and summary."""
        topic = "climate change"
        summary = "Global temperatures are rising"
        result = prompt_service.generate_reflect_prompt(topic, summary)

        # Topic should be in system message
        assert topic in result[0].content
        # Summary should be in human message
        assert summary in result[1].content

    def test_generate_reflect_prompt_asks_for_knowledge_gap(self, prompt_service):
        """Test reflect prompt asks for knowledge gap identification."""
        result = prompt_service.generate_reflect_prompt("test", "summary")
        # Should ask to identify knowledge gap
        assert "knowledge gap" in result[1].content.lower()

    def test_prompt_templates_render_correctly(self, prompt_service):
        """Test that all Jinja templates render without errors."""
        # Query prompt
        query_messages = prompt_service.generate_query_prompt("test topic")
        assert len(query_messages[0].content) > 0

        # Summarize prompt
        summarize_messages = prompt_service.generate_summarize_prompt(
            "test topic", "", "context"
        )
        assert len(summarize_messages[0].content) > 0

        # Reflect prompt
        reflect_messages = prompt_service.generate_reflect_prompt(
            "test topic", "summary"
        )
        assert len(reflect_messages[0].content) > 0
