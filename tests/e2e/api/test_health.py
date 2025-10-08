import pytest

@pytest.mark.asyncio
async def test_health_check(http_client, api_config):
    """Test the /health endpoint returns ok status."""
    response = await http_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"