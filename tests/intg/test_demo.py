import os
import tempfile

import pytest

from demo.example import main


class TestDemo:
    """Integration tests for the demo functionality."""

    @pytest.mark.asyncio
    async def test_demo_execution(self):
        """Test that the demo runs successfully and produces output."""
        # Create a temporary file for output
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as temp_file:
            temp_path = temp_file.name

        try:
            # Run the demo with the temporary file
            await main(output_file=temp_path)

            # Check that the file was created and has content
            assert os.path.exists(temp_path)
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check basic structure
            assert (
                "# Current state of AI technology in Japan and future prospects"
                in content
            )
            assert "## Summary" in content
            assert "**Success:** True" in content

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_demo_with_debug_mode(self, monkeypatch):
        """Test demo execution in debug mode."""
        # Set RESEARCH_API_DEBUG environment variable
        monkeypatch.setenv("RESEARCH_API_DEBUG", "true")

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as temp_file:
            temp_path = temp_file.name

        await main(output_file=temp_path)

        assert os.path.exists(temp_path)
        with open(temp_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert (
            "# Current state of AI technology in Japan and future prospects" in content
        )
        assert "**Success:** True" in content

        if os.path.exists(temp_path):
            os.unlink(temp_path)
