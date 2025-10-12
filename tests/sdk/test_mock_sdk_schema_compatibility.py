"""Tests for verifying mock SDK schema compatibility with production API."""

import pytest
from pydantic import ValidationError

from src.olm_d_rch.api.schemas import ResearchResponse
from mock_olm_d_rch_client.mock_olm_d_rch_client import MockOlmDRchClient


class TestMockSdkSchemaCompatibility:
    """Test suite for mock SDK schema compatibility."""

    def test_research_response_schema_compatibility(self):
        """Test that mock research response matches ResearchResponse schema."""
        client = MockOlmDRchClient()
        query = "test query"

        # Call mock research method
        response_dict = client.research(query)

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

    def test_research_method_signature_difference(self):
        """Test that highlights the difference in method signatures."""
        client = MockOlmDRchClient()

        # Mock only accepts query, not backend
        # This test documents the incompatibility
        response = client.research("test")

        # Check that backend is not handled (mock doesn't accept it)
        # In production, backend is optional in request
        # But mock doesn't support it at all
        assert "backend" not in response  # Mock response doesn't include backend info

        # Note: This test passes but documents the limitation
        # In a real scenario, you might want to update mock to accept backend