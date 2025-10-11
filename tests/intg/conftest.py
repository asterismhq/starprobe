"""Integration test specific fixtures."""

import pytest

from tests.envs import setup_intg_test_env


@pytest.fixture(scope="function", autouse=True)
def set_intg_test_env(monkeypatch):
    """Setup environment variables for integration tests."""
    setup_intg_test_env(monkeypatch)
