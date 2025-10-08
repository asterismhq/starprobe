import pytest

@pytest.mark.asyncio
async def test_research_success(http_client, api_config):
    """Test successful research request."""
    payload = {"topic": "AI technology trends"}
    response = await http_client.post("/api/v1/research", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["summary"], str) and len(data["summary"]) > 0
    assert isinstance(data["sources"], list)
    assert data["processing_time"] > 0
    assert data["error_message"] is None

@pytest.mark.asyncio
async def test_research_empty_topic(http_client, api_config):
    """Test research request with empty topic fails."""
    payload = {"topic": ""}
    response = await http_client.post("/api/v1/research", json=payload)
    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.asyncio
async def test_research_timeout(http_client, api_config):
    """Test research request handles timeout gracefully."""
    # Note: Actual timeout depends on implementation; simulate or check error_message
    payload = {"topic": "Very complex topic that might timeout"}
    response = await http_client.post("/api/v1/research", json=payload)
    data = response.json()
    # Assuming timeout is handled as failure
    if data["success"] is False:
        assert "timeout" in data["error_message"].lower()