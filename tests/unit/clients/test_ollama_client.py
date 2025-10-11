"""Unit tests for OllamaClient."""

from unittest.mock import Mock, patch

import pytest

from olm_d_rch.clients.ollama_client import (
    OllamaClient,
    OllamaClientAdapter,
)


class TestOllamaClientAdapter:
    """Test cases for OllamaClientAdapter."""

    @pytest.mark.asyncio
    async def test_adapter_invoke_delegates(self):
        """Test adapter delegates invoke to wrapped client."""
        mock_chat_ollama = Mock()
        mock_chat_ollama.invoke.return_value = "response"

        adapter = OllamaClientAdapter(mock_chat_ollama)
        result = await adapter.invoke(["message"], key="value")

        mock_chat_ollama.invoke.assert_called_once_with(["message"], key="value")
        assert result == "response"

    def test_adapter_bind_tools_returns_new_adapter(self):
        """Test bind_tools returns new adapter wrapping bound client."""
        mock_chat_ollama = Mock()
        mock_bound_client = Mock()
        mock_chat_ollama.bind_tools.return_value = mock_bound_client

        adapter = OllamaClientAdapter(mock_chat_ollama)
        tools = [Mock()]
        result = adapter.bind_tools(tools)

        # Should call bind_tools on wrapped client
        mock_chat_ollama.bind_tools.assert_called_once_with(tools)
        # Should return new adapter wrapping the bound client
        assert isinstance(result, OllamaClientAdapter)
        assert result._client == mock_bound_client


class TestOllamaClient:
    """Test cases for OllamaClient."""

    @patch("langchain_ollama.ChatOllama")
    def test_init_with_defaults(self, mock_chat_ollama):
        """Test client initialization with default settings."""
        from olm_d_rch.config.ollama_settings import OllamaSettings

        settings = OllamaSettings(ollama_host="http://mock-ollama:11434/")
        client = OllamaClient(settings)

        assert client.base_url == "http://mock-ollama:11434"
        assert client.temperature == 0

        # Verify ChatOllama was called with correct parameters
        mock_chat_ollama.assert_called_once_with(
            base_url="http://mock-ollama:11434/",
            model=client.model,
            temperature=0,
        )

    @patch("langchain_ollama.ChatOllama")
    def test_init_creates_adapter(self, mock_chat_ollama):
        """Test initialization creates OllamaClientAdapter."""
        from olm_d_rch.config.ollama_settings import OllamaSettings

        settings = OllamaSettings()
        client = OllamaClient(settings)

        assert hasattr(client, "_client")
        assert isinstance(client._client, OllamaClientAdapter)

    @pytest.mark.asyncio
    @patch("langchain_ollama.ChatOllama")
    async def test_invoke_delegates_to_adapter(self, mock_chat_ollama):
        """Test invoke delegates to internal adapter."""
        from olm_d_rch.config.ollama_settings import OllamaSettings

        mock_response = Mock()
        mock_chat_instance = mock_chat_ollama.return_value
        mock_chat_instance.invoke.return_value = mock_response

        settings = OllamaSettings()
        client = OllamaClient(settings)
        messages = ["test message"]
        result = await client.invoke(messages, extra_param="value")

        # Should delegate to adapter's invoke
        mock_chat_instance.invoke.assert_called_once_with(messages, extra_param="value")
        assert result == mock_response
