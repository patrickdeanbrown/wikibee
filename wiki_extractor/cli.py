from __future__ import annotations

import json
import logging
import os
from types import SimpleNamespace
from typing import Optional, Tuple

import requests
import typer

from . import formatting as _formatting
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

app = typer.Typer()


# ANSI color codes for terminal output
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    END = "\033[0m"


def _handle_search(search_term: str, args) -> Optional[str]:
    """Handle search term input and return selected article URL."""
    client = WikiClient()

    try:
        results = client.search_articles(search_term, limit=10, timeout=args.timeout)
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Search failed: {e}{Colors.END}")
        return None

    if not results:
        print(f"{Colors.YELLOW}No results found for '{search_term}'{Colors.END}")
        print(f"{Colors.CYAN}Try different search terms or check spelling.{Colors.END}")
        return None

    if len(results) == 1:
        result = results[0]
        print(f"{Colors.GREEN}Found exact match: \"{result['title']}\"{Colors.END}")
        print(f"{Colors.CYAN}Extracting article...{Colors.END}")
        return result["url"]

    # Multiple results - show menu unless --yolo
    if args.yolo:
        result = results[0]
        print(f"{Colors.MAGENTA}Auto-selected: \"{result['title']}\"{Colors.END}")
        return result["url"]

    return _show_search_menu(results, search_term)


def _show_search_menu(results: list[dict], search_term: str) -> Optional[str]:
    """Display interactive search menu and return selected URL."""
    print(
        f"\n{Colors.BOLD}{Colors.BLUE}Found {len(results)} results for "
        f"'{search_term}':{Colors.END}\n"
    )

    for i, result in enumerate(results, 1):
        title = result["title"]
        desc = result.get("description", "").strip()

        # Highlight first result and number others
        if i == 1:
            print(f"{Colors.BOLD}{Colors.GREEN}1. {title}{Colors.END}")
        else:
            print(f"{Colors.BOLD}{i}. {title}{Colors.END}")

        if desc:
            print(f"   {Colors.CYAN}{desc}{Colors.END}")
        print()

    while True:
        try:
            prompt = (
                f"{Colors.YELLOW}Enter your choice (1-{len(results)}) or "
                f"'q' to quit: {Colors.END}"
            )
            choice = input(prompt).strip().lower()

            if choice == "q":
                print(f"{Colors.MAGENTA}Cancelled{Colors.END}")
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(results):
                selected = results[choice_num - 1]
                print(f"{Colors.GREEN}Selected: {selected['title']}{Colors.END}")
                return selected["url"]
            else:
                print(
                    f"{Colors.RED}Please enter a number between 1 and "
                    f"{len(results)}{Colors.END}"
                )
        except ValueError:
            print(f"{Colors.RED}Please enter a valid number or 'q' to quit{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n{Colors.MAGENTA}Cancelled{Colors.END}")
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


def _process_page(p: dict, convert_numbers_for_tts: bool, raise_on_error: bool):
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
    session: Optional[object] = None,
    raise_on_error: bool = False,
) -> Tuple[Optional[str], Optional[str]]:
    final_page_title: Optional[str] = None

    client = WikiClient(session)

    title = _parse_title(url)

    try:
        data = client.fetch_page(url, title, lead_only, timeout)
    except requests.exceptions.RequestException as e:  # type: ignore[name-defined]
        logger.error("Network error: %s", e)
        if raise_on_error:
            raise NetworkError(e)
        return None, final_page_title
    except json.JSONDecodeError as e:
        logger.error("API returned invalid JSON: %s", e)
        if raise_on_error:
            raise APIError(e)
        return None, final_page_title

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        logger.warning("No pages found in API response")
        return None, final_page_title

    page_obj = next(iter(pages.values()))
    return _process_page(page_obj, convert_numbers_for_tts, raise_on_error)


@app.command()
def main(
    article: str = typer.Argument(..., help="Wikipedia article URL or search term"),
    output_dir: str = typer.Option(
        os.path.join(os.getcwd(), "output"),
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
    tts_voice: str = typer.Option(
        "af_sky+af_bella",
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
    tts_normalize: bool = typer.Option(
        False,
        "--tts-normalize",
        help=(
            "Apply text normalization for better TTS pronunciation "
            "(e.g., 'Richard III' → 'Richard the third')"
        ),
    ),
):
    args = SimpleNamespace(
        article=article,
        output_dir=output_dir,
        filename=filename,
        no_save=no_save,
        timeout=timeout,
        lead_only=lead_only,
        tts_file=tts,
        heading_prefix=heading_prefix,
        verbose=verbose,
        tts_audio=audio,
        tts_server=tts_server,
        tts_voice=tts_voice,
        tts_format=tts_format,
        yolo=yolo,
        tts_normalize=tts_normalize,
    )

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
        url = _handle_search(article_input, args)
        if url is None:
            raise typer.Exit(code=1)
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


def _produce_audio(
    markdown_content: str,
    md_path: str,
    out_dir: str,
    args,
):
    audio_ext = "." + args.tts_format
    audio_path = os.path.splitext(md_path)[0] + audio_ext
    text_source = _build_tts_text(markdown_content, args)
    try:
        saved = _synthesize_audio(text_source, audio_path, out_dir, args)
        logger.info("Saved audio to %s", saved)
        print(f"Audio saved to: {saved}")
    except TTSClientError as e:
        logger.error("Failed to synthesize audio: %s", e)


def _build_tts_text(markdown_content: str, args) -> str:
    # Apply TTS normalization if requested
    if args.tts_normalize:
        normalized_content = tts_normalize_for_tts(markdown_content)
    else:
        normalized_content = markdown_content

    # Apply TTS-friendly formatting
    if args.tts_file:
        return make_tts_friendly(normalized_content, heading_prefix=args.heading_prefix)
    return make_tts_friendly(normalized_content)


def _synthesize_audio(text: str, audio_path: str, out_dir: str, args) -> str:
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
    args,
    markdown_content: str,
    md_path: str,
    out_dir: str,
    page_title: str,
) -> None:
    """Write markdown and optional TTS text/audio outputs."""
    if args.no_save:
        print(markdown_content)
        return

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    logger.info("Saved markdown to %s", md_path)
    print(f"Output saved to: {md_path}")

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
        print(f"TTS-friendly copy saved to: {tts_path}")

    if args.tts_audio:
        _produce_audio(markdown_content, md_path, out_dir, args)


if __name__ == "__main__":
    app()
