"""Unit tests for NexusSettings."""

from src.starprobe.config.nexus_settings import NexusSettings


class TestNexusSettings:
    """Test cases for NexusSettings."""

    def test_default_values(self, monkeypatch):
        """Test that default values are set correctly."""
        monkeypatch.delenv("STARPROBE_USE_MOCK_NEXUS", raising=False)
        settings = NexusSettings()
        assert settings.nexus_base_url == "http://localhost:8000"
        assert settings.nexus_timeout == 30.0
        assert settings.use_mock_nexus is False

    def test_env_var_override(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("NEXUS_BASE_URL", "http://example.com:9000")
        monkeypatch.setenv("NEXUS_TIMEOUT", "60.0")
        monkeypatch.setenv("STARPROBE_USE_MOCK_NEXUS", "true")

        settings = NexusSettings()
        assert settings.nexus_base_url == "http://example.com:9000"
        assert settings.nexus_timeout == 60.0
        assert settings.use_mock_nexus is True

    def test_use_mock_bool_parsing(self, monkeypatch):
        """Test boolean parsing for use_mock_nexus."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
        ]

        for env_value, expected in test_cases:
            monkeypatch.setenv("STARPROBE_USE_MOCK_NEXUS", env_value)
            settings = NexusSettings()
            assert settings.use_mock_nexus is expected

    def test_timeout_type_conversion(self, monkeypatch):
        """Test that timeout is correctly converted to float."""
        monkeypatch.setenv("NEXUS_TIMEOUT", "45")
        settings = NexusSettings()
        assert isinstance(settings.nexus_timeout, float)
        assert settings.nexus_timeout == 45.0
