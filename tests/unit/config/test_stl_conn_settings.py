"""Unit tests for StlConnSettings."""

from src.starprobe.config.stl_conn_settings import StlConnSettings


class TestStlConnSettings:
    """Test cases for StlConnSettings."""

    def test_default_values(self, monkeypatch):
        """Test that default values are set correctly."""
        monkeypatch.delenv("STARPROBE_USE_MOCK_STL_CONN", raising=False)
        settings = StlConnSettings()
        assert settings.stl_conn_base_url == "http://localhost:8000"
        assert settings.stl_conn_timeout == 30.0
        assert settings.use_mock_stl_conn is False

    def test_env_var_override(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("STL_CONN_BASE_URL", "http://example.com:9000")
        monkeypatch.setenv("STL_CONN_TIMEOUT", "60.0")
        monkeypatch.setenv("STARPROBE_USE_MOCK_STL_CONN", "true")

        settings = StlConnSettings()
        assert settings.stl_conn_base_url == "http://example.com:9000"
        assert settings.stl_conn_timeout == 60.0
        assert settings.use_mock_stl_conn is True

    def test_use_mock_bool_parsing(self, monkeypatch):
        """Test boolean parsing for use_mock_stl_conn."""
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
            monkeypatch.setenv("STARPROBE_USE_MOCK_STL_CONN", env_value)
            settings = StlConnSettings()
            assert settings.use_mock_stl_conn is expected

    def test_timeout_type_conversion(self, monkeypatch):
        """Test that timeout is correctly converted to float."""
        monkeypatch.setenv("STL_CONN_TIMEOUT", "45")
        settings = StlConnSettings()
        assert isinstance(settings.stl_conn_timeout, float)
        assert settings.stl_conn_timeout == 45.0
