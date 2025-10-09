"""Integration test specific fixtures."""

import pytest


@pytest.fixture(autouse=True)
def set_debug_mode(monkeypatch):
    """Automatically set DEBUG=true for all integration tests."""
    monkeypatch.setenv("DEBUG", "true")
