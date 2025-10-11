import importlib
from importlib import import_module

import pytest

from dev.mocks.mock_ollama_client import MockOllamaClient
from dev.mocks.mock_scraping_service import MockScrapingService
from dev.mocks.mock_search_client import MockSearchClient
from olm_d_rch.clients import DdgsClient, OllamaClient
from olm_d_rch.services import ScrapingService

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


def _refresh_dependency_container_module():
    """Reload config and container modules so new env vars take effect."""

    workflow_settings_module = import_module("olm_d_rch.config.workflow_settings")
    importlib.reload(workflow_settings_module)

    config_module = import_module("olm_d_rch.config")
    importlib.reload(config_module)

    container_module = import_module("olm_d_rch.container")
    return importlib.reload(container_module)


@pytest.mark.parametrize("env_var, attribute, mock_cls, real_cls", _COMPONENT_MATRIX)
@pytest.mark.parametrize("use_mock", [True, False])
def test_dependency_container_switches_between_mock_and_real(
    monkeypatch, env_var, attribute, mock_cls, real_cls, use_mock
):
    """DependencyContainer should select mock or real implementations per flag."""

    for variable, *_ in _COMPONENT_MATRIX:
        monkeypatch.setenv(
            variable, "True" if variable == env_var and use_mock else "False"
        )

    container_module = _refresh_dependency_container_module()
    container = container_module.DependencyContainer()

    instance = getattr(container, attribute)
    expected_cls = mock_cls if use_mock else real_cls

    assert isinstance(
        instance, expected_cls
    ), f"Expected {attribute} to be {expected_cls.__name__} when {env_var}={use_mock}"
