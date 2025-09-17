from __future__ import annotations

from pathlib import Path
from typing import Dict

import typer
from rich.console import Console

from .. import config
from .extract import (
    DEFAULT_HEADING_PREFIX,
    DEFAULT_SEARCH_LIMIT,
    DEFAULT_TIMEOUT,
    DEFAULT_TTS_AUDIO,
    DEFAULT_TTS_FILE,
    DEFAULT_TTS_FORMAT,
    DEFAULT_TTS_NORMALIZE,
    DEFAULT_TTS_SERVER,
    DEFAULT_TTS_VOICE,
    DEFAULT_VERBOSE,
    DEFAULT_YOLO,
)

console = Console()
config_app = typer.Typer(help="Manage wikibee configuration")


def register_config(app: typer.Typer) -> None:
    app.add_typer(config_app, name="config")


def _toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def _toml_dump_sections(sections: Dict[str, Dict[str, object]]) -> str:
    lines: list[str] = []
    for section, values in sections.items():
        filtered = {k: v for k, v in values.items() if v is not None}
        if not filtered:
            continue
        lines.append(f"[{section}]")
        for key, value in filtered.items():
            lines.append(f"{key} = {_toml_value(value)}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


@config_app.command("init")
def config_init(
    force: bool = typer.Option(False, "--force", help="Overwrite if exists")
) -> None:
    """Create a default config file at the standard location."""
    path = config.get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        console.print(
            f"[yellow]Config already exists at {path}. Use --force to overwrite.[/]"
        )
        raise typer.Exit(code=1)

    default_sections: Dict[str, Dict[str, object]] = {
        "general": {
            "output_dir": str(Path.home() / "wikibee"),
            "default_timeout": DEFAULT_TIMEOUT,
            "lead_only": False,
            "no_save": False,
            "verbose": DEFAULT_VERBOSE,
        },
        "tts": {
            "server_url": DEFAULT_TTS_SERVER,
            "default_voice": DEFAULT_TTS_VOICE,
            "format": DEFAULT_TTS_FORMAT,
            "normalize": DEFAULT_TTS_NORMALIZE,
            "file": DEFAULT_TTS_FILE,
            "audio": DEFAULT_TTS_AUDIO,
        },
        "search": {
            "auto_select": DEFAULT_YOLO,
            "search_limit": DEFAULT_SEARCH_LIMIT,
        },
    }

    heading_prefix_default = DEFAULT_HEADING_PREFIX
    if heading_prefix_default:
        default_sections["tts"]["heading_prefix"] = heading_prefix_default

    content = _toml_dump_sections(default_sections)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    console.print(f"Default configuration file created at {path}")
