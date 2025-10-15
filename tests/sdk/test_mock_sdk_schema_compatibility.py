"""Tests for verifying mock SDK schema compatibility with production API."""

from starprobe_sdk import MockResearchApiClient, ResearchResponse


class TestMockSdkSchemaCompatibility:
    """Test suite for mock SDK schema compatibility."""

    def test_research_response_schema_compatibility(self):
        """Test that mock research response matches ResearchResponse schema."""
        client = MockResearchApiClient()
        topic = "test topic"

        # Call mock research method
        response = client.research(topic)

        # Validate response is ResearchResponse instance
        assert isinstance(response, ResearchResponse)
        assert response.success is True
        assert response.article is not None
        assert response.metadata is not None
        assert response.error_message is None
        assert response.diagnostics == []
        assert response.processing_time == 0.1

    def test_research_method_signature(self):
        """Test the method signature."""
        client = MockResearchApiClient()

        # Mock accepts topic
        response = client.research("test")

        # Check response structure
        assert isinstance(response, ResearchResponse)
        assert response.success is True
        assert response.article is not None
        assert response.metadata is not None
