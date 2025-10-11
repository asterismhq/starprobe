# ollama-deep-researcher/tests/e2e/conftest.py
import pytest

from tests.envs import setup_e2e_test_env


@pytest.fixture(scope="function", autouse=True)
def set_e2e_test_env(monkeypatch):
    """Setup environment variables for E2E tests."""
    setup_e2e_test_env(monkeypatch)
