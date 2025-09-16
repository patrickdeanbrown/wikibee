# Configuration management for wikibee
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Dict

import platformdirs

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def get_config_path() -> Path:
    """
    Returns the platform-specific path for the configuration file.

    Returns:
        Path: The path to the configuration file.
    """
    return Path(platformdirs.user_config_path("wikibee")) / "config.toml"


def _normalize_config_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize nested configuration sections into flat keys."""

    flat: Dict[str, Any] = {
        key: value for key, value in data.items() if not isinstance(value, Mapping)
    }

    section_mappings = {
        "general": {
            "output_dir": "output_dir",
            "default_timeout": "timeout",
            "timeout": "timeout",
            "verbose": "verbose",
            "lead_only": "lead_only",
        },
        "tts": {
            "server_url": "tts_server",
            "base_url": "tts_server",
            "default_voice": "tts_voice",
            "voice": "tts_voice",
            "format": "tts_format",
            "heading_prefix": "heading_prefix",
            "normalize": "tts_normalize",
        },
        "search": {
            "auto_select": "yolo",
            "search_limit": "search_limit",
        },
    }

    for section, mapping in section_mappings.items():
        section_values = data.get(section)
        if not isinstance(section_values, Mapping):
            continue
        for key, target_key in mapping.items():
            if key in section_values:
                flat[target_key] = section_values[key]

    return flat


def load_config() -> Dict[str, Any]:
    """
    Loads the configuration from the TOML file.

    Returns:
        dict: The configuration dictionary, or an empty dict if not found.
    """
    config_path = get_config_path()
    if not config_path.exists():
        return {}
    with open(config_path, "rb") as f:
        parsed: Dict[str, Any] = tomllib.load(f)
    return _normalize_config_data(parsed)


def merge_configs(
    defaults: Dict[str, Any],
    config_file: Dict[str, Any],
    cli_args: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Merges configurations from defaults, config file, and CLI arguments.

    Args:
        defaults: Dictionary of default values.
        config_file: Dictionary of values from the config file.
        cli_args: Dictionary of values from the command line.

    Returns:
        dict: The merged configuration.
    """
    merged = defaults.copy()
    merged.update(config_file)

    for key, value in cli_args.items():
        if value is None:
            continue
        merged[key] = value
    return merged
