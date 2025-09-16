from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Final, List, Optional, Tuple

import click
import requests
import typer
from rich.console import Console
from typer.core import TyperGroup

from . import config  # re-exported for tests to monkeypatch
from . import formatting as _formatting
from ._types import ExtractsResponse, PageObject, SearchResult
from .client import WikiClient
from .tts_normalizer import normalize_for_tts as tts_normalize_for_tts
from .tts_openai import TTSClientError, TTSOpenAIClient

# Re-export frequently used formatting helpers for backward compatibility.
# Import the module and assign names so linters don't report unused imports.
sanitize_filename = _formatting.sanitize_filename
normalize_for_tts = _formatting.normalize_for_tts
make_tts_friendly = _formatting.make_tts_friendly
INFLECT_AVAILABLE = _formatting.INFLECT_AVAILABLE
write_text_file = _formatting.write_text_file

logger = logging.getLogger(__name__)


class _DefaultGroup(TyperGroup):
    """Click Group that treats non-command first argument as default command."""

    default_command_name = "extract"

    def resolve_command(
        self, ctx: click.Context, args: List[str]
    ) -> Tuple[Optional[str], Optional[click.Command], List[str]]:
        if (
            args
            and args[0] not in self.commands
            and self.default_command_name in self.commands
        ):
            args = [self.default_command_name] + args
        return super().resolve_command(ctx, args)


app = typer.Typer(cls=_DefaultGroup, no_args_is_help=True)
console = Console()

DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "output")
DEFAULT_SEARCH_LIMIT: Final[int] = 10
DEFAULT_TIMEOUT: Final[int] = 15
DEFAULT_LEAD_ONLY: Final[bool] = False
DEFAULT_TTS_VOICE: Final[str] = "af_sky+af_bella"
DEFAULT_TTS_FORMAT: Final[str] = "mp3"
DEFAULT_TTS_SERVER: Final[str] = "http://localhost:8880/v1"
DEFAULT_FILENAME: Final[Optional[str]] = None
DEFAULT_NO_SAVE: Final[bool] = False
DEFAULT_VERBOSE: Final[bool] = False
DEFAULT_HEADING_PREFIX: Final[Optional[str]] = None
DEFAULT_TTS_FILE: Final[bool] = False
DEFAULT_TTS_AUDIO: Final[bool] = False
DEFAULT_YOLO: Final[bool] = False
DEFAULT_TTS_NORMALIZE: Final[bool] = False

DEFAULTS: Dict[str, object] = {
    # CLI/config defaults (CLI args override these; config can override defaults)
    "timeout": DEFAULT_TIMEOUT,
    "lead_only": DEFAULT_LEAD_ONLY,
    "tts_voice": DEFAULT_TTS_VOICE,
    "tts_format": DEFAULT_TTS_FORMAT,
    "tts_server": DEFAULT_TTS_SERVER,
    "output_dir": DEFAULT_OUTPUT_DIR,
    "filename": DEFAULT_FILENAME,
    "no_save": DEFAULT_NO_SAVE,
    "verbose": DEFAULT_VERBOSE,
    "heading_prefix": DEFAULT_HEADING_PREFIX,
    "tts_file": DEFAULT_TTS_FILE,
    "tts_audio": DEFAULT_TTS_AUDIO,
    "yolo": DEFAULT_YOLO,
    "search_limit": DEFAULT_SEARCH_LIMIT,
    "tts_normalize": DEFAULT_TTS_NORMALIZE,
}


@dataclass
class Args:
    article: str
    output_dir: str
    filename: Optional[str]
    no_save: bool
    timeout: int
    lead_only: bool
    tts_file: bool
    heading_prefix: Optional[str]
    verbose: bool
    tts_audio: bool
    tts_server: str
    tts_voice: Optional[str]
    tts_format: str
    yolo: bool
    search_limit: int
    tts_normalize: bool


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
            return default
    return default


def _coerce_str(value: object, default: str) -> str:
    if value is None:
        return default
    return str(value)


def _coerce_optional_str(value: object, default: Optional[str]) -> Optional[str]:
    if value is None:
        return default
    return str(value)


def _handle_search(search_term: str, args: Args) -> Optional[str]:
    """Handle search term input and return selected article URL."""
    client = WikiClient()

    raw_limit = getattr(args, "search_limit", DEFAULT_SEARCH_LIMIT)
    try:
        search_limit = int(raw_limit)
    except (TypeError, ValueError):
        search_limit = DEFAULT_SEARCH_LIMIT
    if search_limit <= 0:
        search_limit = DEFAULT_SEARCH_LIMIT
    try:
        results = client.search_articles(
            search_term, limit=search_limit, timeout=args.timeout
        )
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Search failed: {e}[/]")
        return None

    if not results:
        console.print(f"[yellow]No results found for '{search_term}'[/]")
        console.print("[cyan]Try different search terms or check spelling.[/]")
        return None

    if len(results) == 1:
        result = results[0]
        console.print(f"[green]Found exact match: \"{result['title']}\"[/]")
        console.print("[cyan]Extracting article...[/]")
        return result["url"]

    # Multiple results - show menu unless --yolo
    if args.yolo:
        result = results[0]
        console.print(f"[magenta]Auto-selected: \"{result['title']}\"[/]")
        return result["url"]

    return _show_search_menu(results, search_term)


def _collect_cli_overrides(
    ctx: click.Context, raw_cli_values: Dict[str, Tuple[str, object]]
) -> Dict[str, object]:
    """Return CLI values that should override config values."""

    overrides: Dict[str, object] = {}
    get_source = getattr(ctx, "get_parameter_source", None)
    if callable(get_source):
        override_names = {"COMMANDLINE", "ENVIRONMENT"}
        for param_name, (config_key, value) in raw_cli_values.items():
            if value is None:
                continue
            source = get_source(param_name)
            source_name = getattr(source, "name", None)
            if isinstance(source_name, str) and source_name.upper() in override_names:
                overrides[config_key] = value
        return overrides

    for _, (config_key, value) in raw_cli_values.items():  # pragma: no cover
        if value is None:
            continue
        default_value = DEFAULTS.get(config_key)
        if default_value is not None and value == default_value:
            continue
        overrides[config_key] = value
    return overrides


def _build_args_from_merged(article: str, merged: Dict[str, object]) -> Args:
    """Construct the runtime Args from merged configuration values."""

    output_dir_value = os.path.expanduser(
        str(merged.get("output_dir", DEFAULT_OUTPUT_DIR))
    )
    return Args(
        article=article,
        output_dir=output_dir_value,
        filename=_coerce_optional_str(merged.get("filename"), DEFAULT_FILENAME),
        no_save=_coerce_bool(merged.get("no_save"), DEFAULT_NO_SAVE),
        timeout=_coerce_int(merged.get("timeout"), DEFAULT_TIMEOUT),
        lead_only=_coerce_bool(merged.get("lead_only"), DEFAULT_LEAD_ONLY),
        tts_file=_coerce_bool(merged.get("tts_file"), DEFAULT_TTS_FILE),
        heading_prefix=_coerce_optional_str(
            merged.get("heading_prefix"), DEFAULT_HEADING_PREFIX
        ),
        verbose=_coerce_bool(merged.get("verbose"), DEFAULT_VERBOSE),
        tts_audio=_coerce_bool(merged.get("tts_audio"), DEFAULT_TTS_AUDIO),
        tts_server=_coerce_str(merged.get("tts_server"), DEFAULT_TTS_SERVER),
        tts_voice=_coerce_optional_str(merged.get("tts_voice"), DEFAULT_TTS_VOICE),
        tts_format=_coerce_str(merged.get("tts_format"), DEFAULT_TTS_FORMAT),
        yolo=_coerce_bool(merged.get("yolo"), DEFAULT_YOLO),
        search_limit=_coerce_int(merged.get("search_limit"), DEFAULT_SEARCH_LIMIT),
        tts_normalize=_coerce_bool(merged.get("tts_normalize"), DEFAULT_TTS_NORMALIZE),
    )


def _show_search_menu(results: List[SearchResult], search_term: str) -> Optional[str]:
    """Display interactive search menu and return selected URL."""
    console.print(
        f"\n[bold blue]Found {len(results)} results for '{search_term}':[/]\n"
    )

    for i, result in enumerate(results, 1):
        title = result["title"]
        desc = result.get("description", "").strip()

        # Highlight first result and number others
        if i == 1:
            console.print(f"[bold green]1. {title}[/]")
        else:
            console.print(f"[bold]{i}. {title}[/]")

        if desc:
            console.print(f"   [cyan]{desc}[/]")
        console.print()

    while True:
        try:
            prompt = f"[yellow]Enter your choice (1-{len(results)}) or 'q' to quit: [/]"
            choice = console.input(prompt).strip().lower()

            if choice == "q":
                console.print("[magenta]Cancelled[/]")
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(results):
                selected = results[choice_num - 1]
                console.print(f"[green]Selected: {selected['title']}[/]")
                return selected["url"]
            else:
                console.print(
                    f"[red]Please enter a number between 1 and {len(results)}[/]"
                )
        except ValueError:
            console.print("[red]Please enter a valid number or 'q' to quit[/]")
        except KeyboardInterrupt:
            console.print("\n[magenta]Cancelled[/]")
            return None


# Structured exceptions
class NetworkError(RuntimeError):
    """Network-related errors (requests exceptions)"""


class APIError(RuntimeError):
    """API returned invalid data or JSON decoding failed"""


class NotFoundError(RuntimeError):
    """Page not found or no extract available"""


class DisambiguationError(RuntimeError):
    """Raised when the requested title is a disambiguation page."""


def _parse_title(u: str) -> str:
    from urllib.parse import unquote, urlparse

    parsed = urlparse(u)
    if not parsed.scheme:
        raise ValueError("URL must include scheme (http:// or https://)")

    path = parsed.path or ""
    wiki_prefix = "/wiki/"
    title = None
    if wiki_prefix in path:
        title = path.split(wiki_prefix, 1)[1]
    else:
        if path and path.strip("/"):
            title = path.strip("/").split("/")[-1]

    if title:
        return unquote(title)
    raise ValueError("Could not determine page title from URL")


def _process_page(
    p: PageObject, convert_numbers_for_tts: bool, raise_on_error: bool
) -> Tuple[Optional[str], Optional[str]]:
    pageprops = p.get("pageprops") or {}
    if "disambiguation" in pageprops:
        final_title = p.get("title")
        logger.info("Disambiguation page detected for: %s", final_title)
        if raise_on_error:
            raise DisambiguationError(f"Title '{final_title}' is a disambiguation page")
        return None, final_title

    final_title = p.get("title")
    extract_text = p.get("extract")
    if extract_text is None:
        logger.warning("No extract text present for page: %s", final_title)
        if raise_on_error:
            raise NotFoundError(f"No extract text present for page: {final_title}")
        return None, final_title

    out_text = normalize_for_tts(extract_text, convert_numbers=convert_numbers_for_tts)
    return out_text, final_title


def extract_wikipedia_text(
    url: str,
    convert_numbers_for_tts: bool = False,
    timeout: int = 15,
    lead_only: bool = False,
    session: Optional[requests.Session] = None,
    raise_on_error: bool = False,
) -> Tuple[Optional[str], Optional[str]]:
    final_page_title: Optional[str] = None

    client = WikiClient(session)

    title = _parse_title(url)

    try:
        data: ExtractsResponse = client.fetch_page(url, title, lead_only, timeout)
    except requests.exceptions.RequestException as e:
        logger.error("Network error: %s", e)
        if raise_on_error:
            raise NetworkError(e)
        return None, final_page_title
    except json.JSONDecodeError as e:
        logger.error("API returned invalid JSON: %s", e)
        if raise_on_error:
            raise APIError(e)
        return None, final_page_title

    pages = (data.get("query") or {}).get("pages") or {}
    if not pages:
        logger.warning("No pages found in API response")
        return None, final_page_title

    page_obj = next(iter(pages.values()))
    return _process_page(page_obj, convert_numbers_for_tts, raise_on_error)


@app.command(name="extract", help="Extract a Wikipedia article to Markdown/TTS")
def extract(
    article: str = typer.Argument(..., help="Wikipedia article URL or search term"),
    output_dir: str = typer.Option(
        DEFAULT_OUTPUT_DIR,
        "-o",
        "--output",
        "--output-dir",
        help="Directory to save output",
    ),
    filename: Optional[str] = typer.Option(
        None,
        "-f",
        "--filename",
        help="Base filename to use (otherwise derived from title)",
    ),
    no_save: bool = typer.Option(
        False,
        "-n",
        "--no-save",
        help="Do not save to file; print to stdout",
    ),
    timeout: int = typer.Option(
        15,
        "-t",
        "--timeout",
        help="HTTP timeout seconds",
    ),
    lead_only: bool = typer.Option(
        False,
        "-l",
        "--lead-only",
        help="Fetch only the lead (intro) section",
    ),
    tts: bool = typer.Option(
        False,
        "--tts",
        "--tts-file",
        help="Also produce a TTS-friendly .txt alongside the .md",
    ),
    heading_prefix: Optional[str] = typer.Option(
        None,
        "--heading-prefix",
        help="Prefix for headings in TTS file, e.g. 'Section:'",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Verbose logging",
    ),
    audio: bool = typer.Option(
        False,
        "--audio",
        "--tts-audio",
        help="Also produce an audio file via the local Kokoro/OpenAI-compatible TTS",
    ),
    tts_server: str = typer.Option(
        "http://localhost:8880/v1",
        "--tts-server",
        help="Base URL of the local TTS server (OpenAI-compatible)",
    ),
    tts_voice: Optional[str] = typer.Option(
        None,
        "--tts-voice",
        help="Voice identifier for the TTS engine",
    ),
    tts_format: str = typer.Option(
        "mp3",
        "--tts-format",
        help="Audio output format",
    ),
    yolo: bool = typer.Option(
        False,
        "-y",
        "--yolo",
        help="Auto-select first search result without prompting",
    ),
    search_limit: int = typer.Option(
        DEFAULT_SEARCH_LIMIT,
        "--search-limit",
        min=1,
        help="Maximum number of search results to fetch when searching",
    ),
    tts_normalize: bool = typer.Option(
        False,
        "--tts-normalize",
        help=(
            "Apply text normalization for better TTS pronunciation "
            "(e.g., 'Richard III' → 'Richard the third')"
        ),
    ),
) -> None:
    ctx = click.get_current_context()

    raw_cli_values: Dict[str, Tuple[str, object]] = {
        "timeout": ("timeout", timeout),
        "lead_only": ("lead_only", lead_only),
        "tts_voice": ("tts_voice", tts_voice),
        "tts_format": ("tts_format", tts_format),
        "tts_server": ("tts_server", tts_server),
        "output_dir": ("output_dir", output_dir),
        "filename": ("filename", filename),
        "no_save": ("no_save", no_save),
        "heading_prefix": ("heading_prefix", heading_prefix),
        "verbose": ("verbose", verbose),
        "tts": ("tts_file", tts),
        "audio": ("tts_audio", audio),
        "yolo": ("yolo", yolo),
        "search_limit": ("search_limit", search_limit),
        "tts_normalize": ("tts_normalize", tts_normalize),
    }

    cli_overrides = _collect_cli_overrides(ctx, raw_cli_values)
    cfg = config.load_config()
    merged = config.merge_configs(DEFAULTS, cfg, cli_overrides)
    args = _build_args_from_merged(article, merged)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    article_input = args.article

    # Determine if input is URL or search term
    if article_input.startswith(("http://", "https://")):
        # It's a URL - proceed with existing logic
        url = article_input
        logger.info("Attempting to extract text from: %s", url)
    else:
        # It's a search term - perform search first
        url_opt = _handle_search(article_input, args)
        if url_opt is None:
            raise typer.Exit(code=1)
        url = url_opt
        logger.info("Extracting article: %s", url)

    result_text, page_title = extract_wikipedia_text(
        url,
        convert_numbers_for_tts=False,
        timeout=args.timeout,
        lead_only=args.lead_only,
    )

    if result_text is None:
        logger.error("Failed to extract text from URL")
        raise typer.Exit(code=1)

    base_name = args.filename or page_title or "wikipedia_article"
    safe_base = sanitize_filename(base_name)
    md_name = safe_base + ".md"
    out_dir = os.path.abspath(args.output_dir)
    os.makedirs(out_dir, exist_ok=True)

    md_path = os.path.join(out_dir, md_name)
    if os.path.exists(md_path):
        for i in range(1, 1000):
            candidate = os.path.join(out_dir, f"{safe_base}_{i}.md")
            if not os.path.exists(candidate):
                md_path = candidate
                break

    markdown_content = f"# {page_title}\n\n{result_text}\n"
    try:
        _write_outputs(args, markdown_content, md_path, out_dir, page_title)
    except IOError as e:
        logger.error("Failed to write output: %s", e)


app.command(name="main", hidden=True)(extract)


def _produce_audio(
    markdown_content: str,
    md_path: str,
    out_dir: str,
    args: Args,
) -> None:
    audio_ext = "." + args.tts_format
    audio_path = os.path.splitext(md_path)[0] + audio_ext
    text_source = _build_tts_text(markdown_content, args)
    try:
        saved = _synthesize_audio(text_source, audio_path, out_dir, args)
        logger.info("Saved audio to %s", saved)
        console.print(f"Audio saved to: {saved}")
    except TTSClientError as e:
        logger.error("Failed to synthesize audio: %s", e)


def _build_tts_text(markdown_content: str, args: Args) -> str:
    # Apply TTS normalization if requested
    if args.tts_normalize:
        normalized_content = tts_normalize_for_tts(markdown_content)
    else:
        normalized_content = markdown_content

    # Apply TTS-friendly formatting
    if args.tts_file:
        return make_tts_friendly(normalized_content, heading_prefix=args.heading_prefix)
    return make_tts_friendly(normalized_content)


def _synthesize_audio(text: str, audio_path: str, out_dir: str, args: Args) -> str:
    tts_client = TTSOpenAIClient(base_url=args.tts_server)
    return tts_client.synthesize_to_file(
        text,
        dest_path=audio_path,
        base_dir=out_dir,
        model="kokoro",
        voice=args.tts_voice,
        file_format=args.tts_format,
    )


def _write_outputs(
    args: Args,
    markdown_content: str,
    md_path: str,
    out_dir: str,
    page_title: Optional[str],
) -> None:
    """Write markdown and optional TTS text/audio outputs."""
    if args.no_save:
        console.print(markdown_content)
        return

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    logger.info("Saved markdown to %s", md_path)
    console.print(f"Output saved to: {md_path}")

    if args.tts_file:
        # Apply normalization if requested
        if args.tts_normalize:
            content_for_tts = tts_normalize_for_tts(markdown_content)
        else:
            content_for_tts = markdown_content
        tts_text = make_tts_friendly(
            content_for_tts, heading_prefix=args.heading_prefix
        )
        tts_path = os.path.splitext(md_path)[0] + ".txt"
        with open(tts_path, "w", encoding="utf-8") as f:
            f.write(tts_text)
        logger.info("Saved TTS-friendly text to %s", tts_path)
        console.print(f"TTS-friendly copy saved to: {tts_path}")

    if args.tts_audio:
        _produce_audio(markdown_content, md_path, out_dir, args)


# -----------------
# Config subcommands
# -----------------
config_app = typer.Typer(help="Manage wikibee configuration")


def _toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def _toml_dump_sections(sections: Dict[str, Dict[str, object]]) -> str:
    lines: List[str] = []
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
            "lead_only": DEFAULT_LEAD_ONLY,
            "no_save": DEFAULT_NO_SAVE,
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


app.add_typer(config_app, name="config")

if __name__ == "__main__":
    app()
