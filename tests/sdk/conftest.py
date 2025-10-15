# ollama-deep-researcher/tests/sdk/conftest.py
import pytest


@pytest.fixture(scope="function", autouse=True)
def set_sdk_test_env(monkeypatch):
    """Setup environment variables for SDK tests.

    Note: Monkeypatch only works for in-process code execution.
    For subprocess-based tests (intg/e2e), use subprocess env parameter.
    """
    # Set environment variables to use mocks for SDK testing
    monkeypatch.setenv("STL_CONN_USE_MOCK_OLLAMA", "True")
    monkeypatch.setenv("STARPROBE_USE_MOCK_SEARCH", "True")
    monkeypatch.setenv("STARPROBE_USE_MOCK_SCRAPING", "True")
    # Add any other necessary mock flags
    monkeypatch.setenv("STARPROBE_OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("OLLAMA_HOST", "http://mock-ollama:11434")
