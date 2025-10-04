"""Unit tests for OllamaClient."""

import pytest

from ollama_deep_researcher.clients.ollama_client import (
    OllamaClient,
    OllamaClientAdapter,
)


class TestOllamaClientAdapter:
    """Test cases for OllamaClientAdapter."""

    def test_adapter_invoke_delegates(self, mocker):
        """Test adapter delegates invoke to wrapped client."""
        mock_chat_ollama = mocker.Mock()
        mock_chat_ollama.invoke.return_value = "response"

        adapter = OllamaClientAdapter(mock_chat_ollama)
        result = adapter.invoke(["message"], key="value")

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
        assert client.base_url == "http://localhost:11434/"
        assert client.model == "llama3.2:3b"
        assert client.temperature == 0
        assert client.format is None

        # Verify ChatOllama was called with correct parameters
        mock_chat_ollama.assert_called_once_with(
            base_url="http://localhost:11434/",
            model="llama3.2:3b",
            temperature=0,
        )

    def test_init_with_custom_settings(self, mock_settings, mock_chat_ollama):
        """Test client initialization with custom parameters."""
        client = OllamaClient(
            mock_settings,
            base_url="http://custom:11434/",
            model="llama3.1",
            temperature=0.7,
            format="json",
        )

        assert client.base_url == "http://custom:11434/"
        assert client.model == "llama3.1"
        assert client.temperature == 0.7
        assert client.format == "json"

        # Verify ChatOllama was called with custom parameters
        mock_chat_ollama.assert_called_once_with(
            base_url="http://custom:11434/",
            model="llama3.1",
            temperature=0.7,
            format="json",
        )

    def test_init_creates_adapter(self, mock_settings, mock_chat_ollama):
        """Test initialization creates OllamaClientAdapter."""
        client = OllamaClient(mock_settings)

        assert hasattr(client, "_client")
        assert isinstance(client._client, OllamaClientAdapter)

    def test_configure_updates_client(self, mock_settings, mock_chat_ollama):
        """Test configure updates internal client."""
        client = OllamaClient(mock_settings)

        # Reset mock to clear initialization call
        mock_chat_ollama.reset_mock()

        client.configure(
            base_url="http://new:11434/", model="new-model", temperature=0.5
        )

        # Verify settings were updated
        assert client.base_url == "http://new:11434/"
        assert client.model == "new-model"
        assert client.temperature == 0.5

        # Verify ChatOllama was called again with new settings
        mock_chat_ollama.assert_called_once_with(
            base_url="http://new:11434/", model="new-model", temperature=0.5
        )

    def test_configure_with_json_format(self, mock_settings, mock_chat_ollama):
        """Test configure with JSON format."""
        client = OllamaClient(mock_settings)
        mock_chat_ollama.reset_mock()

        client.configure(format="json")

        # Verify format was updated and passed to ChatOllama
        assert client.format == "json"
        mock_chat_ollama.assert_called_once_with(
            base_url="http://localhost:11434/",
            model="llama3.2:3b",
            temperature=0,
            format="json",
        )

    def test_configure_partial_update(self, mock_settings, mock_chat_ollama):
        """Test configure with partial parameter update."""
        client = OllamaClient(mock_settings, model="original-model")
        mock_chat_ollama.reset_mock()

        # Only update model, keep other settings
        client.configure(model="new-model")

        assert client.model == "new-model"
        assert client.base_url == "http://localhost:11434/"  # Unchanged
        assert client.temperature == 0  # Unchanged

        mock_chat_ollama.assert_called_once_with(
            base_url="http://localhost:11434/", model="new-model", temperature=0
        )

    def test_invoke_delegates_to_adapter(self, mock_settings, mock_chat_ollama, mocker):
        """Test invoke delegates to internal adapter."""
        mock_response = mocker.Mock()
        mock_chat_instance = mock_chat_ollama.return_value
        mock_chat_instance.invoke.return_value = mock_response

        client = OllamaClient(mock_settings)
        messages = ["test message"]
        result = client.invoke(messages, extra_param="value")

        # Should delegate to adapter's invoke
        mock_chat_instance.invoke.assert_called_once_with(messages, extra_param="value")
        assert result == mock_response

    def test_format_none_excludes_format_kwarg(self, mock_settings, mock_chat_ollama):
        """Test that format kwarg is excluded when format is None."""
        OllamaClient(mock_settings, format=None)

        # Get the kwargs passed to ChatOllama
        call_kwargs = mock_chat_ollama.call_args.kwargs

        # format should not be in kwargs
        assert "format" not in call_kwargs

    def test_format_set_includes_format_kwarg(self, mock_settings, mock_chat_ollama):
        """Test that format kwarg is included when format is set."""
        OllamaClient(mock_settings, format="json")

        # Get the kwargs passed to ChatOllama
        call_kwargs = mock_chat_ollama.call_args.kwargs

        # format should be in kwargs
        assert "format" in call_kwargs
        assert call_kwargs["format"] == "json"

    def test_configure_none_values_ignored(self, mock_settings, mock_chat_ollama):
        """Test configure ignores None parameters but re-initializes client."""
        client = OllamaClient(
            mock_settings,
            base_url="http://original:11434/",
            model="original-model",
            temperature=0.5,
        )

        original_base_url = client.base_url
        original_model = client.model
        original_temp = client.temperature

        # Reset mock to check for re-initialization
        mock_chat_ollama.reset_mock()

        # Configure with all None - should not change attributes but should re-init client
        client.configure(base_url=None, model=None, temperature=None, format=None)

        assert client.base_url == original_base_url
        assert client.model == original_model
        assert client.temperature == original_temp

        # Verify the client was re-initialized with the original parameters
        mock_chat_ollama.assert_called_once_with(
            base_url=original_base_url,
            model=original_model,
            temperature=original_temp,
        )
