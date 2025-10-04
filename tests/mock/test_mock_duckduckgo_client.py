import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dev.mocks.mock_duckduckgo_client import MockDuckDuckGoClient
from ollama_deep_researcher.clients.duckduckgo_client import DuckDuckGoClient


def test_real_client():
    """Test real DuckDuckGoClient."""
    print("Testing real DuckDuckGoClient:")
    real_client = DuckDuckGoClient()
    real_result = real_client.search("Python programming", max_results=2)
    print("Real result structure:")
    print(real_result)
    print(
        "Keys in first result:",
        (
            list(real_result["results"][0].keys())
            if real_result["results"]
            else "No results"
        ),
    )
    # Assert that the result is a dict with 'results' key
    assert isinstance(real_result, dict)
    assert "results" in real_result
    assert isinstance(real_result["results"], list)


def test_mock_client():
    """Test MockDuckDuckGoClient."""
    print("\nTesting MockDuckDuckGoClient:")
    mock_client = MockDuckDuckGoClient()
    mock_result = mock_client.search("Python programming", max_results=2)
    print("Mock result structure:")
    print(mock_result)
    print("Keys in first result:", list(mock_result["results"][0].keys()))
    # Assert that the result is a dict with 'results' key
    assert isinstance(mock_result, dict)
    assert "results" in mock_result
    assert isinstance(mock_result["results"], list)


def compare_structures(real_result, mock_result):
    """Compare real and mock result structures."""
    print("\nComparison:")
    print("Real results count:", len(real_result["results"]))
    print("Mock results count:", len(mock_result["results"]))

    if real_result["results"] and mock_result["results"]:
        real_keys = set(real_result["results"][0].keys())
        mock_keys = set(mock_result["results"][0].keys())
        print("Real result keys:", real_keys)
        print("Mock result keys:", mock_keys)
        print("Keys match:", real_keys == mock_keys)
        return real_keys == mock_keys
    return False


def test_multiple_queries():
    """Test multiple queries with different parameters."""
    print("\n\nTesting multiple queries:")
    real_client = DuckDuckGoClient()
    mock_client = MockDuckDuckGoClient()

    queries = [
        ("machine learning", 3),
        ("web development", 1),
        ("data science", 5),
    ]

    for query, max_results in queries:
        print(f"\nQuery: '{query}', max_results: {max_results}")
        real_result = real_client.search(query, max_results=max_results)
        mock_result = mock_client.search(query, max_results=max_results)

        print(f"  Real returned {len(real_result['results'])} results")
        print(f"  Mock returned {len(mock_result['results'])} results")
        print(
            f"  Max results respected: Real={len(real_result['results']) <= max_results}, Mock={len(mock_result['results']) <= max_results}"
        )


if __name__ == "__main__":
    real_result = test_real_client()
    mock_result = test_mock_client()
    structures_match = compare_structures(real_result, mock_result)
    test_multiple_queries()

    print("\n" + "=" * 50)
    print(f"Overall result: {'PASS' if structures_match else 'FAIL'}")
    print("=" * 50)
