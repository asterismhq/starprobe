"""Tests for verifying mock SDK schema compatibility with production API."""

import pytest
from pydantic import ValidationError

from sdk.olm_d_rch_sdk import MockResearchApiClient
from src.olm_d_rch.api.schemas import ResearchResponse


class TestMockSdkSchemaCompatibility:
    """Test suite for mock SDK schema compatibility."""

    def test_research_response_schema_compatibility(self):
        """Test that mock research response matches ResearchResponse schema."""
        client = MockResearchApiClient()
        topic = "test topic"

        # Call mock research method
        response_dict = client.research(topic)

        # Validate response against ResearchResponse schema
        try:
            research_response = ResearchResponse(**response_dict)
            assert research_response.success is True
            assert research_response.article is not None
            assert research_response.metadata is not None
            assert research_response.error_message is None
            assert research_response.diagnostics == []
            assert research_response.processing_time == 0.1
        except ValidationError as e:
            pytest.fail(f"Mock response does not match ResearchResponse schema: {e}")

    def test_research_method_signature(self):
        """Test the method signature."""
        client = MockResearchApiClient()

        # Mock accepts topic
        response = client.research("test")

        # Check response structure
        assert response["success"] is True
        assert "article" in response
        assert "metadata" in response
