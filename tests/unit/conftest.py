# ollama-deep-researcher/tests/unit/conftest.py
import pytest


@pytest.fixture(scope="function", autouse=True)
def set_unit_test_env(monkeypatch):
    """Setup environment variables for unit tests.

    Note: Monkeypatch only works for in-process code execution.
    For subprocess-based tests (intg/e2e), use subprocess env parameter.
    """
    monkeypatch.setenv("OLM_D_RCH_OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("OLLAMA_HOST", "http://mock-ollama:11434")
    monkeypatch.setenv("USE_MOCK_OLLAMA", "True")
    monkeypatch.setenv("USE_MOCK_SEARCH", "True")
    monkeypatch.setenv("USE_MOCK_SCRAPING", "True")
