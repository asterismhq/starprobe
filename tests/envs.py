# ollama-deep-researcher/tests/envs.py

"""Environment variable configuration for different test categories."""


def setup_unit_test_env(monkeypatch):
    """Setup environment variables for unit tests."""
    monkeypatch.setenv("RESEARCH_API_OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("OLLAMA_HOST", "http://mock-ollama:11434")
    monkeypatch.setenv("USE_MOCK_OLLAMA", "False")
    monkeypatch.setenv("USE_MOCK_SEARCH", "False")
    monkeypatch.setenv("USE_MOCK_SCRAPING", "False")


def setup_intg_test_env(monkeypatch):
    """Setup environment variables for integration tests."""
    monkeypatch.setenv("RESEARCH_API_OLLAMA_MODEL", "tinyllama:1.1b")
    monkeypatch.setenv("OLLAMA_HOST", "http://mock-ollama:11434")
    monkeypatch.setenv("USE_MOCK_OLLAMA", "True")
    monkeypatch.setenv("USE_MOCK_SEARCH", "True")
    monkeypatch.setenv("USE_MOCK_SCRAPING", "True")


def setup_e2e_test_env(monkeypatch):
    """Setup environment variables for E2E tests."""
    monkeypatch.setenv("RESEARCH_API_OLLAMA_MODEL", "tinyllama:1.1b")
    monkeypatch.setenv("USE_MOCK_OLLAMA", "False")
    monkeypatch.setenv("USE_MOCK_SEARCH", "False")
    monkeypatch.setenv("USE_MOCK_SCRAPING", "False")
