# ollama-deep-researcher/tests/unit/conftest.py
import json

import pytest
from stl_conn_sdk.stl_conn_client import MockStlConnClient, SimpleResponseStrategy


@pytest.fixture(scope="function", autouse=True)
def set_unit_test_env(monkeypatch):
    """Setup environment variables for unit tests.

    Note: Monkeypatch only works for in-process code execution.
    For subprocess-based tests (intg/e2e), use subprocess env parameter.
    """
    monkeypatch.setenv("STARPROBE_OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("OLLAMA_HOST", "http://mock-ollama:11434")
    monkeypatch.setenv("STL_CONN_USE_MOCK_OLLAMA", "True")
    monkeypatch.setenv("STARPROBE_USE_MOCK_SEARCH", "True")
    monkeypatch.setenv("STARPROBE_USE_MOCK_SCRAPING", "True")
    monkeypatch.setenv(
        "STARPROBE_USE_MOCK_STL_CONN", "True"
    )  # Enable mock LLM for unit tests


@pytest.fixture
def mock_llm_json():
    """Mock LLM client that returns JSON string content (for JSON-mode nodes)."""
    json_content = json.dumps({"query": "test query", "rationale": "test rationale"})
    strategy = SimpleResponseStrategy(content=json_content)
    return MockStlConnClient(response_format="langchain", strategy=strategy)


@pytest.fixture
def mock_llm_tool():
    """Mock LLM client that returns tool calls (for tool-calling nodes)."""
    strategy = SimpleResponseStrategy(
        content="",  # Empty content when using tool calls
        tool_calls=[
            {
                "name": "Query",
                "args": {"query": "test query", "rationale": "test rationale"},
            }
        ],
    )
    return MockStlConnClient(response_format="langchain", strategy=strategy)


@pytest.fixture
def mock_llm_summary():
    """Mock LLM client that returns summary content (for summarization nodes)."""
    summary_content = "This is a comprehensive test summary of the research results that provides detailed insights and analysis of the topic under investigation, ensuring it exceeds the minimum length requirements for validation."
    strategy = SimpleResponseStrategy(content=summary_content)
    return MockStlConnClient(response_format="langchain", strategy=strategy)
