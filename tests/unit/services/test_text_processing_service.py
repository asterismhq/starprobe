"""Unit tests for TextProcessingService."""

import pytest

from ollama_deep_researcher.services.text_processing_service import (
    TextProcessingService,
)


class TestTextProcessingService:
    """Test cases for TextProcessingService."""

    def test_strip_thinking_tokens(self):
        """Test removal of <thinking> tags."""
        text = "Hello <thinking>internal thought</thinking> world"
        result = TextProcessingService.strip_thinking_tokens(text)
        assert result == "Hello  world"

    def test_strip_thinking_tokens_multiline(self):
        """Test removal of <thinking> tags with multiline content."""
        text = "Start <thinking>line1\nline2\nline3</thinking> end"
        result = TextProcessingService.strip_thinking_tokens(text)
        assert result == "Start  end"

    def test_strip_thinking_tokens_no_tags(self):
        """Test that text without thinking tags is unchanged."""
        text = "Just normal text"
        result = TextProcessingService.strip_thinking_tokens(text)
        assert result == "Just normal text"

    def test_format_sources_with_results(self):
        """Test source list formatting with valid results."""
        search_results = {
            "results": [
                {"url": "https://example.com/1", "title": "Example 1"},
                {"url": "https://example.com/2", "title": "Example 2"},
                {"url": "https://example.com/3", "title": "Example 3"},
            ]
        }
        result = TextProcessingService.format_sources(search_results)
        expected = "https://example.com/1 (Example 1)\nhttps://example.com/2 (Example 2)\nhttps://example.com/3 (Example 3)"
        assert result == expected

    def test_format_sources_empty_results(self):
        """Test formatting with empty results."""
        search_results = {"results": []}
        result = TextProcessingService.format_sources(search_results)
        assert result == ""

    def test_format_sources_no_results_key(self):
        """Test formatting when results key is missing."""
        search_results = {}
        result = TextProcessingService.format_sources(search_results)
        assert result == ""

    def test_format_sources_missing_fields(self):
        """Test formatting when some results have missing fields."""
        search_results = {
            "results": [
                {"url": "https://example.com/1", "title": "Example 1"},
                {"url": "https://example.com/2"},  # Missing title
                {"title": "Example 3"},  # Missing url
            ]
        }
        result = TextProcessingService.format_sources(search_results)
        assert result == "https://example.com/1 (Example 1)"

    def test_truncate_text_by_tokens_under_limit(self):
        """Test text shorter than max_tokens is unchanged."""
        text = "This is a short text."
        max_tokens = 100
        result = TextProcessingService.truncate_text_by_tokens(text, max_tokens)
        assert result == text

    def test_truncate_text_by_tokens_over_limit(self):
        """Test text longer than max_tokens gets truncated."""
        # Create a long text that will exceed token limit
        text = "word " * 1000  # 1000 words
        max_tokens = 10
        result = TextProcessingService.truncate_text_by_tokens(text, max_tokens)
        # Result should be shorter than original
        assert len(result) < len(text)
        # Result should not be empty
        assert len(result) > 0

    def test_truncate_text_by_tokens_exact_limit(self):
        """Test text exactly at max_tokens."""
        text = "word " * 5
        # Get actual token count for this text
        import tiktoken

        encoding = tiktoken.get_encoding(TextProcessingService.DEFAULT_ENCODING)
        actual_tokens = len(encoding.encode(text))
        result = TextProcessingService.truncate_text_by_tokens(text, actual_tokens)
        assert result == text

    def test_truncate_text_by_tokens_empty_text(self):
        """Test truncation with empty text."""
        text = ""
        max_tokens = 100
        result = TextProcessingService.truncate_text_by_tokens(text, max_tokens)
        assert result == ""

    def test_deduplicate_and_format_sources(self, mock_settings):
        """Test deduplication and formatting of sources."""
        search_results = {
            "results": [
                {
                    "url": "https://example.com/1",
                    "raw_content": "Content from source 1",
                },
                {
                    "url": "https://example.com/2",
                    "raw_content": "Content from source 2",
                },
                # Duplicate URL should be filtered
                {
                    "url": "https://example.com/1",
                    "raw_content": "Duplicate content",
                },
            ]
        }
        result = TextProcessingService.deduplicate_and_format_sources(
            search_results, mock_settings
        )
        # Should only have 2 sources (duplicate removed)
        assert "https://example.com/1" in result
        assert "https://example.com/2" in result
        assert "Content from source 1" in result
        assert "Content from source 2" in result
        assert "Duplicate content" not in result
        # Check separator is present
        assert "---" in result

    def test_deduplicate_and_format_sources_with_truncation(self, mock_settings):
        """Test deduplication with token limit truncation."""
        # Create content that will exceed the token limit
        long_content = "word " * 1000
        search_results = {
            "results": [
                {"url": "https://example.com/1", "raw_content": long_content},
            ]
        }
        result = TextProcessingService.deduplicate_and_format_sources(
            search_results, mock_settings
        )
        # Result should be shorter than original content
        assert len(result) < len(long_content) + 100  # +100 for formatting
        assert "https://example.com/1" in result
        assert "Source:" in result
        assert "Content:" in result

    def test_deduplicate_and_format_sources_fallback_to_content(self, mock_settings):
        """Test fallback to 'content' field when 'raw_content' is missing."""
        search_results = {
            "results": [
                {"url": "https://example.com/1", "content": "Content without raw"},
            ]
        }
        result = TextProcessingService.deduplicate_and_format_sources(
            search_results, mock_settings
        )
        assert "https://example.com/1" in result
        assert "Content without raw" in result

    def test_deduplicate_and_format_sources_empty_results(self, mock_settings):
        """Test deduplication with empty results."""
        search_results = {"results": []}
        result = TextProcessingService.deduplicate_and_format_sources(
            search_results, mock_settings
        )
        assert result == ""

    def test_deduplicate_and_format_sources_no_results_key(self, mock_settings):
        """Test deduplication when results key is missing."""
        search_results = {}
        result = TextProcessingService.deduplicate_and_format_sources(
            search_results, mock_settings
        )
        assert result == ""
