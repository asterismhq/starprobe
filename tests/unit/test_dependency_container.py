import importlib
from importlib import import_module

import pytest

from dev.mocks.mock_ollama_client import MockOllamaClient
from dev.mocks.mock_scraping_service import MockScrapingService
from dev.mocks.mock_search_client import MockSearchClient
from olm_d_rch.clients import DdgsClient, OllamaClient
from olm_d_rch.services import ScrapingService


class TestDependencyContainer:
    """Test cases for DependencyContainer mock/real switching."""

    _COMPONENT_MATRIX = (
        (
            "USE_MOCK_OLLAMA",
            "ollama_client",
            MockOllamaClient,
            OllamaClient,
        ),
        (
            "USE_MOCK_SEARCH",
            "search_client",
            MockSearchClient,
            DdgsClient,
        ),
        (
            "USE_MOCK_SCRAPING",
            "scraping_service",
            MockScrapingService,
            ScrapingService,
        ),
    )

    @classmethod
    def _refresh_dependency_container_module(cls):
        """Reload config and container modules so new env vars take effect."""

        # Reload all settings modules
        settings_modules = [
            "olm_d_rch.config.workflow_settings",
            "olm_d_rch.config.ollama_settings",
            "olm_d_rch.config.ddgs_settings",
            "olm_d_rch.config.scraping_settings",
        ]
        for module_name in settings_modules:
            module = import_module(module_name)
            importlib.reload(module)

        config_module = import_module("olm_d_rch.config")
        importlib.reload(config_module)

        container_module = import_module("olm_d_rch.container")
        return importlib.reload(container_module)

    @pytest.mark.parametrize(
        "env_var, attribute, mock_cls, real_cls", _COMPONENT_MATRIX
    )
    @pytest.mark.parametrize("use_mock", [True, False])
    def test_dependency_container_switches_between_mock_and_real(
        self, monkeypatch, env_var, attribute, mock_cls, real_cls, use_mock
    ):
        """DependencyContainer should select mock or real implementations per flag."""

        # Reset all mock env vars to False first
        monkeypatch.setenv("USE_MOCK_OLLAMA", "False")
        monkeypatch.setenv("USE_MOCK_SEARCH", "False")
        monkeypatch.setenv("USE_MOCK_SCRAPING", "False")

        # Set the specific env var to True if use_mock
        if use_mock:
            monkeypatch.setenv(env_var, "True")

        container_module = self._refresh_dependency_container_module()
        container = container_module.DependencyContainer()

        instance = getattr(container, attribute)
        expected_cls = mock_cls if use_mock else real_cls

        assert isinstance(
            instance, expected_cls
        ), f"Expected {attribute} to be {expected_cls.__name__} when {env_var}={use_mock}"
