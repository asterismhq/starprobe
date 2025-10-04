from dev.mocks.mock_duckduckgo_client import MockDuckDuckGoClient
from src.ollama_deep_researcher.clients.duckduckgo_client import DuckDuckGoClient

# Test real client
print("Testing real DuckDuckGoClient:")
real_client = DuckDuckGoClient()
real_result = real_client.search("Python programming", max_results=2)
print("Real result structure:")
print(real_result)
print(
    "Keys in first result:",
    list(real_result["results"][0].keys()) if real_result["results"] else "No results",
)

# Test mock client
print("\nTesting MockDuckDuckGoClient:")
mock_client = MockDuckDuckGoClient()
mock_result = mock_client.search("Python programming", max_results=2)
print("Mock result structure:")
print(mock_result)
print("Keys in first result:", list(mock_result["results"][0].keys()))

# Compare structures
print("\nComparison:")
print("Real results count:", len(real_result["results"]))
print("Mock results count:", len(mock_result["results"]))
if real_result["results"] and mock_result["results"]:
    real_keys = set(real_result["results"][0].keys())
    mock_keys = set(mock_result["results"][0].keys())
    print("Real result keys:", real_keys)
    print("Mock result keys:", mock_keys)
    print("Keys match:", real_keys == mock_keys)
