import pytest

from wikibee.config import RuntimeConfig


def test_runtime_config_from_sources_merges_with_precedence():
    defaults = {
        "timeout": 15,
        "search_limit": 5,
        "tts_voice": "default",
        "tts_format": "mp3",
        "tts_server": "http://localhost",
        "output_dir": "/tmp/out",
        "filename": None,
        "no_save": False,
        "verbose": False,
        "lead_only": False,
        "tts_file": False,
        "tts_audio": False,
        "yolo": False,
        "heading_prefix": None,
        "tts_normalize": False,
    }
    config_file = {
        "timeout": 20,
        "search_limit": 6,
        "tts_voice": "file-voice",
        "tts_audio": True,
    }
    cli_overrides = {
        "timeout": "30",
        "yolo": "true",
        "heading_prefix": "Section:",
    }

    runtime = RuntimeConfig.from_sources(defaults, config_file, cli_overrides)

    assert runtime.timeout == 30  # CLI wins
    assert runtime.search_limit == 6  # config file beats default
    assert runtime.tts_voice == "file-voice"  # config file
    assert runtime.tts_audio is True
    assert runtime.yolo is True
    assert runtime.heading_prefix == "Section:"


def test_runtime_config_validation_rejects_invalid_types():
    defaults = {"timeout": 15, "search_limit": 5}
    config_file = {}
    cli_overrides = {"search_limit": "not-a-number"}

    with pytest.raises(ValueError):
        RuntimeConfig.from_sources(defaults, config_file, cli_overrides)
