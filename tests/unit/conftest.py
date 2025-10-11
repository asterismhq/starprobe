# ollama-deep-researcher/tests/unit/conftest.py
import pytest

from tests.envs import setup_unit_test_env


@pytest.fixture(scope="function", autouse=True)
def set_unit_test_env(monkeypatch):
    """Setup environment variables for unit tests."""
    setup_unit_test_env(monkeypatch)
