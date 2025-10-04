import re
from typing import Any, Dict, List

import tiktoken

from ollama_deep_researcher.settings import OllamaDeepResearcherSettings


class TextProcessingService:
    """A service class for text processing utilities."""

    # gpt-3.5-turbo や gpt-4 で使われているエンコーディングをデフォルトに設定
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
        指定された最大トークン数に基づいてテキストを切り詰めます。

        Args:
            text (str): 切り詰める対象のテキスト
            max_tokens (int): 許容される最大のトークン数

        Returns:
            str: 最大トークン数を超えないように切り詰められたテキスト
        """
        if not text:
            return ""

        try:
            # 指定されたエンコーディングでTokenizerを読み込む
            encoding = tiktoken.get_encoding(TextProcessingService.DEFAULT_ENCODING)
        except Exception:
            # エンコーディングの読み込みに失敗した場合は、フォールバックとして
            # モデル名を指定して読み込む
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

        # テキストをトークンにエンコード
        tokens = encoding.encode(text)

        # トークン数が最大値を超えていなければ、元のテキストをそのまま返す
        if len(tokens) <= max_tokens:
            return text

        # トークン数が最大値を超えている場合は、最大トークン数までで切り詰める
        truncated_tokens = tokens[:max_tokens]

        # 切り詰めたトークンをデコードしてテキストに戻す
        return encoding.decode(truncated_tokens)

    @staticmethod
    def deduplicate_and_format_sources(
        search_results: Dict[str, List[Dict[str, Any]]],
        settings: OllamaDeepResearcherSettings,
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
                # 設定された最大トークン数でコンテンツを切り詰める
                truncated_content = TextProcessingService.truncate_text_by_tokens(
                    content, settings.max_tokens_per_source
                )
                all_content.append(f"Source: {url}\nContent: {truncated_content}\n---")

        return "\n".join(all_content)
