import re
from typing import Any, Dict, List

import tiktoken

from ollama_deep_researcher.config.workflow_settings import WorkflowSettings


class TextProcessingService:
    """A service class for text processing utilities.

    Dependencies:
    - WorkflowSettings: For configuration of token limits
    """

    # Set the encoding used by gpt-3.5-turbo or gpt-4 as default
    DEFAULT_ENCODING = "cl100k_base"

    @staticmethod
    def strip_thinking_tokens(text: str) -> str:
        """Strip <thinking> and </thinking> tokens from a string."""
        return re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL).strip()

    @staticmethod
    def format_sources(search_results: Dict[str, List[Dict[str, Any]]]) -> str:
        """Format search results into a readable string."""
        if not search_results or "results" not in search_results:
            return ""

        source_parts = []
        for r in search_results.get("results", []):
            if r.get("url") and r.get("title"):
                source_parts.append(f"{r['url']} ({r['title']})")
        return "\n".join(source_parts)

    @staticmethod
    def truncate_text_by_tokens(text: str, max_tokens: int) -> str:
        """
        Truncate text based on the specified maximum number of tokens.

        Args:
            text (str): The text to truncate
            max_tokens (int): The maximum number of tokens allowed

        Returns:
            str: The text truncated to not exceed the maximum number of tokens
        """
        if not text:
            return ""

        try:
            # Load the tokenizer with the specified encoding
            encoding = tiktoken.get_encoding(TextProcessingService.DEFAULT_ENCODING)
        except Exception:
            # If loading the encoding fails, fall back to loading by model name
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

        # Encode the text into tokens
        tokens = encoding.encode(text)

        # If the number of tokens does not exceed the maximum, return the original text
        if len(tokens) <= max_tokens:
            return text

        # If the number of tokens exceeds the maximum, truncate to the maximum number of tokens
        truncated_tokens = tokens[:max_tokens]

        # Decode the truncated tokens back to text
        return encoding.decode(truncated_tokens)

    @staticmethod
    def deduplicate_and_format_sources(
        search_results: Dict[str, List[Dict[str, Any]]],
        settings: WorkflowSettings,
    ) -> str:
        """Deduplicate and format search results into a single string."""
        if not search_results or "results" not in search_results:
            return ""

        all_content = []
        seen_urls = set()

        for r in search_results.get("results", []):
            url = r.get("url")
            if url in seen_urls:
                continue
            seen_urls.add(url)

            content = r.get("raw_content", r.get("content", ""))
            if content:
                # Truncate the content to the configured maximum number of tokens
                truncated_content = TextProcessingService.truncate_text_by_tokens(
                    content, settings.max_tokens_per_source
                )
                all_content.append(f"Source: {url}\nContent: {truncated_content}\n---")

        return "\n".join(all_content)
