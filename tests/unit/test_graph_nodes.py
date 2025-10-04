"""Unit tests for LangGraph node functions."""

import pytest
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage

from ollama_deep_researcher.configuration import Configuration
from ollama_deep_researcher.graph import (
    finalize_summary,
    get_llm,
    summarize_sources,
    web_research,
)
from ollama_deep_researcher.state import SummaryState


class TestFinalizeSummary:
    """Tests for the finalize_summary node."""

    def test_finalize_summary_extracts_source_urls(self):
        """Test that finalize_summary extracts URLs from sources_gathered."""
        state = SummaryState(
            research_topic="Test topic",
            running_summary="Test summary with sufficient length " * 10,
            sources_gathered=[
                "https://example.com/article1\nhttps://example.com/article2",
                "https://example.com/article3",
                "Some text\nhttps://example.com/article4",
            ],
        )

        result = finalize_summary(state)

        assert "sources" in result
        assert len(result["sources"]) == 4
        assert "https://example.com/article1" in result["sources"]
        assert "https://example.com/article2" in result["sources"]
        assert "https://example.com/article3" in result["sources"]
        assert "https://example.com/article4" in result["sources"]

    def test_finalize_summary_success_with_valid_data(self):
        """Test success=True when summary and sources are present."""
        state = SummaryState(
            research_topic="Test topic",
            running_summary="This is a comprehensive summary with more than fifty characters in total.",
            sources_gathered=[
                "https://example.com/source1",
                "https://example.com/source2",
            ],
        )

        result = finalize_summary(state)

        assert result["success"] is True
        assert result["error_message"] is None
        assert len(result["sources"]) > 0

    def test_finalize_summary_fails_with_short_summary(self):
        """Test success=False when summary is too short."""
        state = SummaryState(
            research_topic="Test topic",
            running_summary="Short",  # Less than 50 chars
            sources_gathered=["https://example.com/source1"],
        )

        result = finalize_summary(state)

        assert result["success"] is False
        assert "summary" in result["error_message"].lower()

    def test_finalize_summary_fails_with_no_sources(self):
        """Test success=False when no sources are found."""
        state = SummaryState(
            research_topic="Test topic",
            running_summary="This is a comprehensive summary with more than fifty characters in total.",
            sources_gathered=[],  # No sources
        )

        result = finalize_summary(state)

        assert result["success"] is False
        assert "sources" in result["error_message"].lower()

    def test_finalize_summary_fails_with_no_summary(self):
        """Test success=False when summary is None."""
        state = SummaryState(
            research_topic="Test topic",
            running_summary=None,
            sources_gathered=["https://example.com/source1"],
        )

        result = finalize_summary(state)

        assert result["success"] is False
        assert result["error_message"] is not None

    def test_finalize_summary_deduplicates_sources(self):
        """Test that duplicate sources are removed."""
        state = SummaryState(
            research_topic="Test topic",
            running_summary="Test summary with sufficient length " * 10,
            sources_gathered=[
                "https://example.com/article1\nhttps://example.com/article1",
                "https://example.com/article1",
            ],
        )

        result = finalize_summary(state)

        # Should only have one instance of article1
        assert result["sources"].count("https://example.com/article1") == 1


class TestGetLlm:
    """Tests for the get_llm helper function."""

    def test_get_llm_returns_ollama_instance(self):
        """Test that get_llm returns ChatOllama instance."""
        config = Configuration(
            local_llm="llama3.2",
            ollama_base_url="http://localhost:11434/",
            use_tool_calling=False,
        )

        llm = get_llm(config)

        from langchain_ollama import ChatOllama

        assert isinstance(llm, ChatOllama)

    def test_get_llm_with_json_mode(self):
        """Test that get_llm configures JSON mode correctly."""
        config = Configuration(
            local_llm="llama3.2",
            ollama_base_url="http://localhost:11434/",
            use_tool_calling=False,
        )

        llm = get_llm(config)

        # Check that format is set to json
        assert hasattr(llm, "format")
        assert llm.format == "json"

    def test_get_llm_with_tool_calling(self):
        """Test that get_llm works with tool calling mode."""
        config = Configuration(
            local_llm="llama3.2",
            ollama_base_url="http://localhost:11434/",
            use_tool_calling=True,
        )

        llm = get_llm(config)

        from langchain_ollama import ChatOllama

        assert isinstance(llm, ChatOllama)
        # In tool calling mode, format should not be set to json
        assert not hasattr(llm, "format") or llm.format != "json"

    def test_get_llm_uses_correct_config_values(self):
        """Test that get_llm uses provided configuration values."""
        config = Configuration(
            local_llm="custom-model",
            ollama_base_url="http://custom:9999/",
            use_tool_calling=False,
        )

        llm = get_llm(config)

        assert llm.model == "custom-model"
        assert llm.base_url == "http://custom:9999/"


class TestWebResearch:
    """Tests for the web_research node with error handling."""

    @patch("ollama_deep_researcher.graph.duckduckgo_search")
    @patch("ollama_deep_researcher.graph.deduplicate_and_format_sources")
    @patch("ollama_deep_researcher.graph.format_sources")
    def test_web_research_success(
        self, mock_format, mock_dedupe, mock_search, mock_config, mock_scraping_model
    ):
        """Test successful web research execution with scraping."""
        mock_search.return_value = {
            "results": [
                {"url": "https://example.com/1", "content": "Test content", "raw_content": "Test content"}
            ]
        }
        mock_dedupe.return_value = "Formatted search results"
        mock_format.return_value = "https://example.com/1"

        state = SummaryState(
            research_topic="Test topic",
            search_query="test query",
            research_loop_count=1,
        )

        result = web_research(state, mock_config)

        mock_search.assert_called_once_with(query="test query", max_results=3)
        mock_scraping_model.scrape.assert_called_once_with(url="https://example.com/1")
        mock_dedupe.assert_called_once()
        assert "sources_gathered" in result
        assert "research_loop_count" in result
        assert "web_research_results" in result
        assert result["research_loop_count"] == 2

    @patch("ollama_deep_researcher.graph.duckduckgo_search")
    def test_web_research_handles_search_exception(self, mock_search, mock_config):
        """Test that web_research handles search API exceptions."""
        mock_search.side_effect = Exception("Search API failed")

        state = SummaryState(
            research_topic="Test topic",
            search_query="test query",
            research_loop_count=1,
        )

        result = web_research(state, mock_config)

        assert "sources_gathered" in result
        assert "research_loop_count" in result
        assert result["research_loop_count"] == 2
        assert "Error during web research" in result["web_research_results"]

    @patch("ollama_deep_researcher.graph.duckduckgo_search")
    def test_web_research_with_successful_scraping(
        self, mock_search, mock_config, mock_scraping_model
    ):
        """Test web_research with successful scraping of all URLs."""
        from tests.fixtures.mock_responses import MOCK_SEARCH_RESULTS_WITHOUT_RAW_CONTENT
        mock_search.return_value = MOCK_SEARCH_RESULTS_WITHOUT_RAW_CONTENT
        mock_scraping_model.scrape.return_value = "Scraped content"

        state = SummaryState(
            research_topic="Test topic",
            search_query="test query",
            research_loop_count=0,
        )

        result = web_research(state, mock_config)

        assert result["research_loop_count"] == 1
        for r in result["web_research_results"]["results"]:
            assert r["raw_content"] == "Scraped content"

    @patch("ollama_deep_researcher.graph.duckduckgo_search")
    def test_web_research_fallback_to_snippet_on_scrape_failure(
        self, mock_search, mock_config, mock_scraping_model_with_failures, caplog
    ):
        """Test fallback to snippet when scraping fails for some URLs."""
        mock_search.return_value = {
            "results": [
                {"url": "http://success.com", "content": "Snippet 1", "raw_content": "Snippet 1"},
                {"url": "http://fail.com", "content": "Snippet 2", "raw_content": "Snippet 2"},
                {"url": "http://success.com/2", "content": "Snippet 3", "raw_content": "Snippet 3"},
            ]
        }

        state = SummaryState(
            research_topic="Test topic",
            search_query="test query",
            research_loop_count=0,
        )

        result = web_research(state, mock_config)
        
        results = result["web_research_results"]["results"]
        assert results[0]["raw_content"] == "Scraped content from http://success.com"
        assert results[1]["raw_content"] == "Snippet 2"
        assert results[2]["raw_content"] == "Scraped content from http://success.com/2"
        assert "Scraping failed for http://fail.com" in caplog.text

    @patch("ollama_deep_researcher.graph.duckduckgo_search")
    def test_web_research_all_scrapes_fail_uses_all_snippets(
        self, mock_search, mock_config, mock_scraping_model_with_failures, caplog
    ):
        """Test that all snippets are used when all scrapes fail."""
        mock_search.return_value = {
            "results": [
                {"url": "http://fail.com/1", "content": "Snippet 1", "raw_content": "Snippet 1"},
                {"url": "http://fail.com/2", "content": "Snippet 2", "raw_content": "Snippet 2"},
            ]
        }

        state = SummaryState(
            research_topic="Test topic",
            search_query="test query",
            research_loop_count=0,
        )

        result = web_research(state, mock_config)

        results = result["web_research_results"]["results"]
        assert results[0]["raw_content"] == "Snippet 1"
        assert results[1]["raw_content"] == "Snippet 2"
        assert "Scraping failed for http://fail.com/1" in caplog.text
        assert "Scraping failed for http://fail.com/2" in caplog.text

    @patch("ollama_deep_researcher.graph.tavily_search")
    def test_web_research_tavily_api(
        self, mock_search, mock_config, mock_scraping_model
    ):
        """Test web_research with Tavily API and scraping."""
        mock_config["configurable"]["search_api"] = "tavily"
        mock_search.return_value = {
            "results": [
                {"url": "https://example.com/tavily", "content": "Tavily snippet", "raw_content": "Tavily snippet"}
            ]
        }
        mock_scraping_model.scrape.return_value = "Scraped from Tavily"

        state = SummaryState(
            research_topic="Test topic",
            search_query="test query",
            research_loop_count=0,
        )

        result = web_research(state, mock_config)

        mock_search.assert_called_once_with(query="test query", max_results=3)
        assert result["web_research_results"]["results"][0]["raw_content"] == "Scraped from Tavily"

    @patch("ollama_deep_researcher.graph.perplexity_search")
    def test_web_research_perplexity_api(
        self, mock_search, mock_config, mock_scraping_model
    ):
        """Test web_research with Perplexity API (no scraping)."""
        mock_config["configurable"]["search_api"] = "perplexity"
        mock_search.return_value = {
            "results": [
                {"url": "https://perplexity.ai/1", "content": "Perplexity answer", "raw_content": "Perplexity answer"}
            ]
        }

        state = SummaryState(
            research_topic="Test topic",
            search_query="test query",
            research_loop_count=0,
        )

        result = web_research(state, mock_config)

        mock_search.assert_called_once_with(query="test query", perplexity_search_loop_count=0)
        mock_scraping_model.scrape.assert_not_called()
        assert result["web_research_results"]["results"][0]["raw_content"] == "Perplexity answer"


class TestSummarizeSources:
    """Tests for the summarize_sources node with error handling."""

    @patch("ollama_deep_researcher.graph.ChatOllama")
    def test_summarize_sources_success(self, mock_ollama_class, mock_config):
        """Test successful source summarization."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(
            content="This is a generated summary of the sources."
        )
        mock_ollama_class.return_value = mock_llm

        state = SummaryState(
            research_topic="Test topic",
            web_research_results=["Research result 1", "Research result 2"],
            running_summary=None,
        )

        result = summarize_sources(state, mock_config)

        assert "running_summary" in result
        assert result["running_summary"] is not None
        assert len(result["running_summary"]) > 0

    @patch("ollama_deep_researcher.graph.ChatOllama")
    def test_summarize_sources_updates_existing_summary(
        self, mock_ollama_class, mock_config
    ):
        """Test updating an existing summary with new context."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Updated summary")
        mock_ollama_class.return_value = mock_llm

        state = SummaryState(
            research_topic="Test topic",
            web_research_results=["Old result", "New result"],
            running_summary="Existing summary",
        )

        result = summarize_sources(state, mock_config)

        assert "running_summary" in result
        assert result["running_summary"] == "Updated summary"

    @patch("ollama_deep_researcher.graph.ChatOllama")
    def test_summarize_sources_handles_llm_exception(
        self, mock_ollama_class, mock_config
    ):
        """Test that summarize_sources handles LLM exceptions gracefully."""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("LLM failed")
        mock_ollama_class.return_value = mock_llm

        state = SummaryState(
            research_topic="Test topic",
            web_research_results=["Research result"],
            running_summary="Existing summary",
        )

        result = summarize_sources(state, mock_config)

        # Should return existing summary or fallback instead of raising
        assert "running_summary" in result
        assert result["running_summary"] is not None
