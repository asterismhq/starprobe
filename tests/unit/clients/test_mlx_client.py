"""Unit tests for MLXClient."""

from unittest.mock import Mock, patch

import pytest

from src.olm_d_rch.clients.mlx_client import MLXClient, MLXClientAdapter


class TestMLXClientAdapter:
    """Test cases for MLXClientAdapter."""

    @pytest.mark.asyncio
    async def test_adapter_invoke_delegates(self):
        """Test adapter delegates invoke to wrapped client."""
        mock_chat_mlx = Mock()
        mock_chat_mlx.invoke.return_value = "response"

        adapter = MLXClientAdapter(mock_chat_mlx)
        result = await adapter.invoke(["message"], key="value")

        mock_chat_mlx.invoke.assert_called_once_with(["message"], key="value")
        assert result == "response"

    def test_adapter_bind_tools_returns_new_adapter(self):
        """Test bind_tools returns new adapter wrapping bound client."""
        mock_chat_mlx = Mock()
        mock_bound_client = Mock()
        mock_chat_mlx.bind_tools.return_value = mock_bound_client

        adapter = MLXClientAdapter(mock_chat_mlx)
        tools = [Mock()]
        result = adapter.bind_tools(tools)

        mock_chat_mlx.bind_tools.assert_called_once_with(tools)
        assert isinstance(result, MLXClientAdapter)
        assert result._client == mock_bound_client


class TestMLXClient:
    """Test cases for MLXClient."""

    @patch("langchain_community.chat_models.mlx.ChatMLX")
    def test_init_with_defaults(self, mock_chat_mlx):
        """Test client initialization with default settings."""
        from src.olm_d_rch.config.mlx_settings import MLXSettings

        settings = MLXSettings()
        client = MLXClient(settings)

        assert client.model == settings.mlx_model
        assert client.temperature == settings.temperature

        mock_chat_mlx.assert_called_once_with(
            model=settings.mlx_model,
            temperature=settings.temperature,
        )
        assert isinstance(client._client, MLXClientAdapter)

    @pytest.mark.asyncio
    @patch("langchain_community.chat_models.mlx.ChatMLX")
    async def test_invoke_delegates_to_adapter(self, mock_chat_mlx):
        """Test invoke delegates to internal adapter."""
        from src.olm_d_rch.config.mlx_settings import MLXSettings

        mock_response = Mock()
        mock_chat_instance = mock_chat_mlx.return_value
        mock_chat_instance.invoke.return_value = mock_response

        settings = MLXSettings()
        client = MLXClient(settings)
        messages = ["test message"]

        result = await client.invoke(messages, extra_param="value")

        mock_chat_instance.invoke.assert_called_once_with(messages, extra_param="value")
        assert result == mock_response

    @patch("langchain_community.chat_models.mlx.ChatMLX")
    def test_bind_tools_delegates_and_returns_adapter(self, mock_chat_mlx):
        """Ensure MLXClient.bind_tools delegates to the internal adapter and returns an adapter."""
        # Create a dummy MLXClient with a mock internal adapter
        from src.olm_d_rch.config.mlx_settings import MLXSettings

        settings = MLXSettings()
        client = MLXClient(settings)

        # Replace internal adapter with a mock that has bind_tools
        mock_adapter = Mock()
        mock_bound = Mock()
        mock_adapter.bind_tools.return_value = mock_bound
        client._client = mock_adapter

        tools = [Mock()]
        result = client.bind_tools(tools)

        mock_adapter.bind_tools.assert_called_once_with(tools)
        # Result should be an adapter that wraps the bound client
        assert isinstance(result, MLXClientAdapter)
        assert result._client == mock_bound
