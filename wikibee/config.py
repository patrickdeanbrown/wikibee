"""Configuration management for wikibee."""

from __future__ import annotations

import logging
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Type, cast

import platformdirs

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

logger = logging.getLogger(__name__)


def _coerce_bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return default


def _coerce_int(value: object, default: int) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            raise ValueError(f"Invalid integer value: {value}") from None
    if value is None:
        return default
    raise ValueError(f"Invalid integer value: {value}")


def _coerce_str(value: object, default: str) -> str:
    if value is None:
        return default
    return str(value)


def _coerce_optional_str(value: object, default: Optional[str]) -> Optional[str]:
    if value is None:
        return default
    return str(value)


if sys.version_info >= (3, 10):

    @dataclass(slots=True)
    class RuntimeConfig:
        timeout: int
        lead_only: bool
        tts_voice: Optional[str]
        tts_format: str
        tts_server: str
        output_dir: str
        filename: Optional[str]
        no_save: bool
        verbose: bool
        heading_prefix: Optional[str]
        tts_file: bool
        tts_audio: bool
        yolo: bool
        search_limit: int
        tts_normalize: bool

        @classmethod
        def from_sources(
            cls,
            defaults: Dict[str, object],
            config_file: Dict[str, object],
            cli_args: Dict[str, object],
        ) -> "RuntimeConfig":
            return _build_runtime_config(cls, defaults, config_file, cli_args)

else:

    @dataclass
    class RuntimeConfig:
        timeout: int
        lead_only: bool
        tts_voice: Optional[str]
        tts_format: str
        tts_server: str
        output_dir: str
        filename: Optional[str]
        no_save: bool
        verbose: bool
        heading_prefix: Optional[str]
        tts_file: bool
        tts_audio: bool
        yolo: bool
        search_limit: int
        tts_normalize: bool

        @classmethod
        def from_sources(
            cls,
            defaults: Dict[str, object],
            config_file: Dict[str, object],
            cli_args: Dict[str, object],
        ) -> "RuntimeConfig":
            return _build_runtime_config(cls, defaults, config_file, cli_args)


def _build_runtime_config(
    cls: Type[RuntimeConfig],
    defaults: Dict[str, object],
    config_file: Dict[str, object],
    cli_args: Dict[str, object],
) -> RuntimeConfig:
    merged: Dict[str, object] = defaults.copy()
    merged.update(config_file)
    for key, value in cli_args.items():
        if value is None:
            continue
        merged[key] = value

    try:
        timeout_default = cast(int, defaults["timeout"])
        search_limit_default = cast(int, defaults["search_limit"])
    except KeyError as exc:  # pragma: no cover - developer misuse
        raise ValueError(f"Missing required default value: {exc}") from exc

    timeout = _coerce_int(merged.get("timeout"), timeout_default)
    search_limit = _coerce_int(merged.get("search_limit"), search_limit_default)

    if search_limit <= 0:
        raise ValueError("search_limit must be positive")

    output_dir = str(
        Path(
            _coerce_str(merged.get("output_dir"), str(defaults["output_dir"]))
        ).expanduser()
    )

    return cls(
        timeout=timeout,
        lead_only=_coerce_bool(merged.get("lead_only"), bool(defaults["lead_only"])),
        tts_voice=_coerce_optional_str(
            merged.get("tts_voice"), cast(Optional[str], defaults.get("tts_voice"))
        ),
        tts_format=_coerce_str(
            merged.get("tts_format"), cast(str, defaults["tts_format"])
        ),
        tts_server=_coerce_str(
            merged.get("tts_server"), cast(str, defaults["tts_server"])
        ),
        output_dir=output_dir,
        filename=_coerce_optional_str(
            merged.get("filename"), cast(Optional[str], defaults.get("filename"))
        ),
        no_save=_coerce_bool(merged.get("no_save"), bool(defaults["no_save"])),
        verbose=_coerce_bool(merged.get("verbose"), bool(defaults["verbose"])),
        heading_prefix=_coerce_optional_str(
            merged.get("heading_prefix"),
            cast(Optional[str], defaults.get("heading_prefix")),
        ),
        tts_file=_coerce_bool(merged.get("tts_file"), bool(defaults["tts_file"])),
        tts_audio=_coerce_bool(merged.get("tts_audio"), bool(defaults["tts_audio"])),
        yolo=_coerce_bool(merged.get("yolo"), bool(defaults["yolo"])),
        search_limit=search_limit,
        tts_normalize=_coerce_bool(
            merged.get("tts_normalize"), bool(defaults["tts_normalize"])
        ),
    )


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
            "no_save": "no_save",
            "filename": "filename",
        },
        "tts": {
            "server_url": "tts_server",
            "base_url": "tts_server",
            "default_voice": "tts_voice",
            "voice": "tts_voice",
            "format": "tts_format",
            "heading_prefix": "heading_prefix",
            "normalize": "tts_normalize",
            "file": "tts_file",
            "audio": "tts_audio",
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
    """Load configuration, returning an empty mapping on failure."""

    config_path = get_config_path()
    if not config_path.exists():
        return {}

    try:
        with open(config_path, "rb") as f:
            parsed: Dict[str, Any] = tomllib.load(f)
    except FileNotFoundError:
        # Race between exists() and open(); behave as if file were absent.
        logger.debug("Config file %s disappeared before it could be read", config_path)
        return {}
    except tomllib.TOMLDecodeError as exc:
        logger.warning("Failed to parse config %s: %s", config_path, exc)
        return {}
    except OSError as exc:
        logger.warning("Unable to read config %s: %s", config_path, exc)
        return {}

    return _normalize_config_data(parsed)


def merge_configs(
    defaults: Dict[str, Any],
    config_file: Dict[str, Any],
    cli_args: Dict[str, Any],
) -> RuntimeConfig:
    """Return a validated config model using precedence CLI > file > defaults."""

    return RuntimeConfig.from_sources(defaults, config_file, cli_args)
