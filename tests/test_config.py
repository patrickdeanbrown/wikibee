# Tests for the wikibee configuration module
from pathlib import Path
from unittest.mock import patch

from wikibee import config


def test_get_config_path():
    """Test that get_config_path constructs the path correctly."""
    with patch("platformdirs.user_config_path") as mock_user_config_path:
        mock_user_config_path.return_value = Path("/fake/config/dir/wikibee")
        expected_path = Path("/fake/config/dir/wikibee") / "config.toml"
        assert config.get_config_path() == expected_path


def test_load_config_no_file():
    """Test that loading a non-existent file returns an empty dict."""
    with patch("pathlib.Path.exists", return_value=False):
        result = config.load_config()
        assert result == {}


def test_load_config_with_file(tmp_path):
    """Test that a TOML config file is loaded correctly."""
    config_path = tmp_path / "config.toml"
    config_content = """
    [general]
    default_timeout = 30
    output_dir = "/tmp/wikibee"
    verbose = true
    no_save = true
    filename = "article.md"

    [tts]
    default_voice = "test_voice"
    server_url = "http://localhost:9000"
    format = "wav"
    normalize = true
    heading_prefix = "Section:"
    file = true
    audio = true

    [search]
    auto_select = true
    search_limit = 5
    """
    config_path.write_text(config_content)

    expected_config = {
        "timeout": 30,
        "output_dir": "/tmp/wikibee",
        "verbose": True,
        "no_save": True,
        "filename": "article.md",
        "tts_voice": "test_voice",
        "tts_server": "http://localhost:9000",
        "tts_format": "wav",
        "tts_normalize": True,
        "heading_prefix": "Section:",
        "tts_file": True,
        "tts_audio": True,
        "yolo": True,
        "search_limit": 5,
    }

    with patch("wikibee.config.get_config_path", return_value=config_path):
        loaded_config = config.load_config()
    assert loaded_config == expected_config


def test_load_config_flat_keys_preserved(tmp_path):
    """Flat TOML keys should still be supported for backward compatibility."""
    config_path = tmp_path / "config.toml"
    config_path.write_text("timeout = 45\nlead_only = true\n")

    with patch("wikibee.config.get_config_path", return_value=config_path):
        loaded_config = config.load_config()

    assert loaded_config["timeout"] == 45
    assert loaded_config["lead_only"] is True


def test_load_config_invalid_toml(tmp_path, caplog):
    config_path = tmp_path / "config.toml"
    config_path.write_text("invalid = [this is not toml")

    with patch("wikibee.config.get_config_path", return_value=config_path):
        with caplog.at_level("WARNING"):
            loaded_config = config.load_config()

    assert loaded_config == {}
    assert "Failed to parse config" in " ".join(caplog.messages)


def test_load_config_unreadable_file(tmp_path, monkeypatch, caplog):
    config_path = tmp_path / "config.toml"
    config_path.write_text("timeout = 10")

    class Boom(IOError):
        pass

    def _boom(*args, **kwargs):
        raise Boom("permission denied")

    monkeypatch.setattr(config, "get_config_path", lambda: config_path)
    monkeypatch.setattr("builtins.open", _boom)

    with caplog.at_level("WARNING"):
        loaded = config.load_config()

    assert loaded == {}
    assert "Unable to read config" in " ".join(caplog.messages)


def test_merge_configs():
    """Test that configurations are merged correctly."""
    defaults = {"timeout": 15, "tts_voice": "default_voice"}
    config_file = {"timeout": 30, "output_dir": "/tmp/output"}
    cli_args = {"tts_voice": "cli_voice", "output_dir": "/cli/output"}

    merged = config.merge_configs(defaults, config_file, cli_args)

    assert merged["timeout"] == 30  # from config_file, overrides default
    assert merged["tts_voice"] == "cli_voice"  # from cli_args, overrides default
    assert merged["output_dir"] == "/cli/output"  # from cli_args, overrides config_file


def test_merge_configs_cli_override_with_default_value():
    """CLI values should override config even if they match the defaults."""
    defaults = {"tts_format": "mp3"}
    config_file = {"tts_format": "wav"}
    cli_args = {"tts_format": "mp3"}

    merged = config.merge_configs(defaults, config_file, cli_args)

    assert merged["tts_format"] == "mp3"
