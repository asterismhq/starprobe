"""Unit tests for OllamaClient."""

import pytest

from ollama_deep_researcher.clients.ollama_client import (
    OllamaClient,
    OllamaClientAdapter,
)


class TestOllamaClientAdapter:
    """Test cases for OllamaClientAdapter."""

    async def test_adapter_invoke_delegates(self, mocker):
        """Test adapter delegates invoke to wrapped client."""
        mock_chat_ollama = mocker.Mock()
        mock_chat_ollama.invoke.return_value = "response"

        adapter = OllamaClientAdapter(mock_chat_ollama)
        result = await adapter.invoke(["message"], key="value")

        mock_chat_ollama.invoke.assert_called_once_with(["message"], key="value")
        assert result == "response"

    def test_adapter_bind_tools_returns_new_adapter(self, mocker):
        """Test bind_tools returns new adapter wrapping bound client."""
        mock_chat_ollama = mocker.Mock()
        mock_bound_client = mocker.Mock()
        mock_chat_ollama.bind_tools.return_value = mock_bound_client

        adapter = OllamaClientAdapter(mock_chat_ollama)
        tools = [mocker.Mock()]
        result = adapter.bind_tools(tools)

        # Should call bind_tools on wrapped client
        mock_chat_ollama.bind_tools.assert_called_once_with(tools)
        # Should return new adapter wrapping the bound client
        assert isinstance(result, OllamaClientAdapter)
        assert result._client == mock_bound_client


class TestOllamaClient:
    """Test cases for OllamaClient."""

    @pytest.fixture
    def mock_chat_ollama(self, mocker):
        """Mock ChatOllama class."""
        return mocker.patch("langchain_ollama.ChatOllama")

    def test_init_with_defaults(self, mock_settings, mock_chat_ollama):
        """Test client initialization with default settings."""
        client = OllamaClient(mock_settings)

        assert client.settings == mock_settings
        assert client.base_url == "http://ollama:11434"
        assert client.model == "tinyllama:1.1b"
        assert client.temperature == 0
        assert client.format is None

        # Verify ChatOllama was called with correct parameters
        mock_chat_ollama.assert_called_once_with(
            base_url="http://ollama:11434/",
            model="tinyllama:1.1b",
            temperature=0,
        )

    def test_init_creates_adapter(self, mock_settings, mock_chat_ollama):
        """Test initialization creates OllamaClientAdapter."""
        client = OllamaClient(mock_settings)

        assert hasattr(client, "_client")
        assert isinstance(client._client, OllamaClientAdapter)

    def test_configure_partial_update(self, mock_settings, mock_chat_ollama):
        """Test configure with partial parameter update."""
        client = OllamaClient(mock_settings)
        mock_chat_ollama.reset_mock()

        # Create new settings with updated model
        new_settings = mock_settings.model_copy(update={"local_llm": "new-model"})
        client.configure(new_settings)

        assert client.model == "new-model"
        assert client.base_url == "http://ollama:11434"  # Unchanged
        assert client.temperature == 0  # Unchanged

        mock_chat_ollama.assert_called_once_with(
            base_url="http://ollama:11434/", model="new-model", temperature=0
        )

    async def test_invoke_delegates_to_adapter(
        self, mock_settings, mock_chat_ollama, mocker
    ):
        """Test invoke delegates to internal adapter."""
        mock_response = mocker.Mock()
        mock_chat_instance = mock_chat_ollama.return_value
        mock_chat_instance.invoke.return_value = mock_response

        client = OllamaClient(mock_settings)
        messages = ["test message"]
        result = await client.invoke(messages, extra_param="value")

        # Should delegate to adapter's invoke
        mock_chat_instance.invoke.assert_called_once_with(messages, extra_param="value")
        assert result == mock_response

    def test_configure_none_values_ignored(self, mock_settings, mock_chat_ollama):
        """Test configure with new settings."""
        client = OllamaClient(mock_settings)

        # Reset mock to check for re-initialization
        mock_chat_ollama.reset_mock()

        # Create new settings by copying mock_settings and updating values
        new_settings = mock_settings.model_copy()
        new_settings.ollama_host = "http://updated:11434/"
        new_settings.local_llm = "updated-model"
        client.configure(new_settings)

        assert client.base_url == "http://updated:11434"
        assert client.model == "updated-model"
        assert client.temperature == 0

        # Verify the client was re-initialized with the new parameters
        mock_chat_ollama.assert_called_once_with(
            base_url="http://updated:11434/",
            model="updated-model",
            temperature=0,
        )
