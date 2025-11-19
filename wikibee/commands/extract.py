from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Tuple

import click
import requests
import typer
from rich.console import Console

from .. import config
from .. import formatting as _formatting
from .._types import ExtractsResponse, PageObject, SearchResult
from ..client import WikiClient
from ..services import OutputManager, SearchError, SearchService, TTSService
from ..tts_openai import TTSClientError, TTSOpenAIClient

logger = logging.getLogger(__name__)
console = Console()

# Re-export formatting helpers for backward compatibility.
sanitize_filename = _formatting.sanitize_filename
normalize_for_tts = _formatting.normalize_for_tts
make_tts_friendly = _formatting.make_tts_friendly
split_wikitext_sections = _formatting.split_wikitext_sections
convert_wikitext_headers = _formatting.convert_wikitext_headers
INFLECT_AVAILABLE = _formatting.INFLECT_AVAILABLE
write_text_file = _formatting.write_text_file

DEFAULT_OUTPUT_DIR = str(Path.cwd() / "output")
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


def register_extract(app: typer.Typer) -> None:
    app.command(name="extract", help="Extract a Wikipedia article to Markdown/TTS")(
        extract
    )
    app.command(name="main", hidden=True)(extract)


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
        help="Apply text normalization for better TTS pronunciation",
    ),
    pick: bool = typer.Option(
        False,
        "--pick",
        help="Interactively select sections to extract",
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
    runtime = config.merge_configs(DEFAULTS, cfg, cli_overrides)
    args = Args(
        article=article,
        output_dir=runtime.output_dir,
        filename=runtime.filename,
        no_save=runtime.no_save,
        timeout=runtime.timeout,
        lead_only=runtime.lead_only,
        tts_file=runtime.tts_file,
        heading_prefix=runtime.heading_prefix,
        verbose=runtime.verbose,
        tts_audio=runtime.tts_audio,
        tts_server=runtime.tts_server,
        tts_voice=runtime.tts_voice,
        tts_format=runtime.tts_format,
        yolo=runtime.yolo,
        search_limit=runtime.search_limit,
        tts_normalize=runtime.tts_normalize,
    )

    # If picking, we need raw text to split sections.
    # If M4B is requested, we also need raw text to preserve headers.
    # So if either is true, we fetch raw and handle normalization later.
    should_preserve_headers = args.tts_audio and args.tts_format.lower() == "m4b"
    fetch_raw = pick or should_preserve_headers

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    article_input = args.article

    if article_input.startswith(("http://", "https://")):
        url = article_input
        logger.info("Attempting to extract text from: %s", url)
    else:
        url_opt = _handle_search(article_input, args)
        if url_opt is None:
            raise typer.Exit(code=1)
        url = url_opt
        logger.info("Extracting article: %s", url)

    # If M4B is requested, we want to preserve headers to create chapters.
    # We fetch raw text (normalize=False) and then convert WikiText headers to Markdown.
    # If picking, we also fetch raw text, filter it, and then potentially normalize.

    result_text, page_title = extract_wikipedia_text(
        url,
        convert_numbers_for_tts=False,
        timeout=args.timeout,
        lead_only=args.lead_only,
        normalize=not fetch_raw,
    )

    if result_text is None:
        logger.error("Failed to extract text from URL")
        raise typer.Exit(code=1)

    if pick:
        result_text = _interactive_pick_sections(result_text)
        if not result_text:
            console.print("[yellow]No sections selected. Exiting.[/]")
            raise typer.Exit(code=0)

    # If we fetched raw but didn't want to preserve headers (and didn't pick),
    # we should normalize now.
    # Wait, if pick=True, we fetched raw. Now we have filtered raw text.
    # If should_preserve_headers=False, we should normalize it now.
    if fetch_raw and not should_preserve_headers:
        result_text = normalize_for_tts(result_text, convert_numbers=False)

    if should_preserve_headers:
        # Convert == Header == to ## Header
        result_text = convert_wikitext_headers(result_text)

    markdown_content = f"# {page_title}\n\n{result_text}\n"

    if args.no_save:
        console.print(markdown_content)
        return

    output_manager = OutputManager(args.output_dir, audio_format=args.tts_format)
    paths = output_manager.prepare_paths(page_title or args.article, args.filename)
    output_manager.write_markdown(paths, markdown_content)
    logger.info("Saved markdown to %s", paths.markdown_path)
    console.print(f"Output saved to: {paths.markdown_path}")

    _save_outputs(args, output_manager, paths, markdown_content)


def _save_outputs(
    args: Args,
    output_manager: OutputManager,
    paths: Any,
    markdown_content: str,
) -> None:
    if args.tts_file:
        output_manager.write_tts_copy(
            paths,
            markdown_content,
            heading_prefix=args.heading_prefix,
            normalize=args.tts_normalize,
        )
        logger.info("Saved TTS-friendly text to %s", paths.tts_path)
        console.print(f"TTS-friendly copy saved to: {paths.tts_path}")

    if args.tts_audio:
        tts_client = TTSOpenAIClient(base_url=args.tts_server)
        tts_service = TTSService(
            client=tts_client,
            output_manager=output_manager,
            model="kokoro",
        )
        try:
            saved = tts_service.synthesize_audio(
                markdown=markdown_content,
                paths=paths,
                heading_prefix=args.heading_prefix,
                normalize=args.tts_normalize,
                voice=args.tts_voice,
                file_format=args.tts_format,
            )
            logger.info("Saved audio to %s", saved)
            console.print(f"Audio saved to: {saved}")
        except TTSClientError as exc:
            logger.error("Failed to synthesize audio: %s", exc)


def _collect_cli_overrides(
    ctx: click.Context, raw_cli_values: Dict[str, Tuple[str, object]]
) -> Dict[str, object]:
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


def _handle_search(search_term: str, args: Args) -> Optional[str]:
    service = SearchService(client=WikiClient())

    raw_limit = getattr(args, "search_limit", DEFAULT_SEARCH_LIMIT)
    try:
        search_limit = int(raw_limit)
    except (TypeError, ValueError):
        search_limit = DEFAULT_SEARCH_LIMIT
    if search_limit <= 0:
        search_limit = DEFAULT_SEARCH_LIMIT

    try:
        results = service.search(search_term, limit=search_limit, timeout=args.timeout)
    except SearchError as exc:
        console.print(f"[red]Search failed: {exc}[/]")
        return None

    if not results:
        console.print(f"[yellow]No results found for '{search_term}'[/]")
        console.print("[cyan]Try different search terms or check spelling.[/]")
        return None

    top_result: SearchResult = results[0]

    if len(results) == 1:
        console.print(f"[green]Found exact match: \"{top_result['title']}\"[/]")
        console.print("[cyan]Extracting article...[/]")
        return top_result["url"]

    if args.yolo:
        console.print(f"[magenta]Auto-selected: \"{top_result['title']}\"[/]")
        return top_result["url"]

    return _show_search_menu(results, search_term)


def _interactive_pick_sections(text: str) -> str:
    """Show interactive menu to pick sections from WikiText."""
    sections = split_wikitext_sections(text)
    if not sections:
        return text

    console.print(f"\n[bold blue]Found {len(sections)} sections:[/]\n")

    # Print sections with indices
    for i, (title, _) in enumerate(sections, 1):
        console.print(f"[bold]{i}.[/] {title}")

    console.print(
        "\n[dim]Enter numbers separated by commas (e.g. 1,3,5) or ranges (e.g. 1-4).[/]"
    )
    console.print("[dim]Enter 'all' to select all, or 'q' to quit.[/]")

    while True:
        try:
            choice = console.input("[yellow]Selection: [/]").strip().lower()

            if choice == "q":
                return ""

            if choice == "all" or choice == "":
                return text

            selected_indices = _parse_selection_input(choice)

            # Validate indices
            valid_indices = sorted(
                [i for i in selected_indices if 1 <= i <= len(sections)]
            )

            if not valid_indices:
                console.print("[red]No valid sections selected. Try again.[/]")
                continue

            console.print(f"[green]Selected {len(valid_indices)} sections.[/]")

            return _reconstruct_picked_sections(sections, valid_indices)

        except ValueError:
            console.print(
                "[red]Invalid input. Please use numbers, ranges (1-3), or 'all'.[/]"
            )
        except KeyboardInterrupt:
            return ""


def _parse_selection_input(choice: str) -> set[int]:
    selected_indices: set[int] = set()
    parts = choice.split(",")

    for part in parts:
        part = part.strip()
        if "-" in part:
            start, end = map(int, part.split("-"))
            selected_indices.update(range(start, end + 1))
        else:
            selected_indices.add(int(part))
    return selected_indices


def _reconstruct_picked_sections(
    sections: list[tuple[str, str]], valid_indices: list[int]
) -> str:
    # Reconstruct text
    # We wrap titles in == == to preserve WikiText structure for subsequent processing
    picked_content = []
    for i in valid_indices:
        title, body = sections[i - 1]
        # If it's the Introduction (usually first), it might not have had a header
        # originally, but split_wikitext_sections assigns "Introduction".
        # If we add == Introduction ==, it becomes a header.
        # Standard Wikipedia doesn't have an "Introduction" header.
        # But split_wikitext_sections handles the first chunk as "Introduction".

        if i == 1 and title == "Introduction":
            picked_content.append(body)
        else:
            picked_content.append(f"== {title} ==\n{body}")

    return "\n\n".join(picked_content)


def _show_search_menu(results: List[SearchResult], search_term: str) -> Optional[str]:
    console.print(
        f"\n[bold blue]Found {len(results)} results for '{search_term}':[/]\n"
    )

    for i, result in enumerate(results, 1):
        title = result["title"]
        desc = result.get("description", "").strip()

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
            console.print(f"[red]Please enter a number between 1 and {len(results)}[/]")
        except ValueError:
            console.print("[red]Please enter a valid number or 'q' to quit[/]")
        except KeyboardInterrupt:
            console.print("\n[magenta]Cancelled[/]")
            return None


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
    p: PageObject,
    convert_numbers_for_tts: bool,
    raise_on_error: bool,
    normalize: bool = True,
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

    if normalize:
        out_text = normalize_for_tts(
            extract_text, convert_numbers=convert_numbers_for_tts
        )
    else:
        out_text = extract_text
    return out_text, final_title


def extract_wikipedia_text(
    url: str,
    convert_numbers_for_tts: bool = False,
    timeout: int = 15,
    lead_only: bool = False,
    session: Optional[requests.Session] = None,
    raise_on_error: bool = False,
    normalize: bool = True,
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
    return _process_page(
        page_obj, convert_numbers_for_tts, raise_on_error, normalize=normalize
    )


class NetworkError(RuntimeError):
    """Network-related errors (requests exceptions)"""


class APIError(RuntimeError):
    """API returned invalid data or JSON decoding failed"""


class NotFoundError(RuntimeError):
    """Page not found or no extract available"""


class DisambiguationError(RuntimeError):
    """Raised when the requested title is a disambiguation page."""
