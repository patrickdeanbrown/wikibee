from __future__ import annotations

import argparse
import json
import logging
import os
from typing import Optional, Tuple

from .client import WikiClient
import requests
from . import formatting as _formatting

# Re-export frequently used formatting helpers for backward compatibility.
# Import the module and assign names so linters don't report unused imports.
sanitize_filename = _formatting.sanitize_filename
normalize_for_tts = _formatting.normalize_for_tts
make_tts_friendly = _formatting.make_tts_friendly
INFLECT_AVAILABLE = _formatting.INFLECT_AVAILABLE
write_text_file = _formatting.write_text_file

logger = logging.getLogger(__name__)


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
    from urllib.parse import urlparse, unquote

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
            raise DisambiguationError(
                f"Title '{final_title}' is a disambiguation page"
            )
        return None, final_title

    final_title = p.get("title")
    extract_text = p.get("extract")
    if extract_text is None:
        logger.warning("No extract text present for page: %s", final_title)
        if raise_on_error:
            raise NotFoundError(
                f"No extract text present for page: {final_title}"
            )
        return None, final_title

    out_text = normalize_for_tts(
        extract_text, convert_numbers=convert_numbers_for_tts
    )
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


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Extract plain text from a Wikipedia article"
        )
    )
    parser.add_argument(
        "url",
        help=(
            "Full Wikipedia article URL (include https://)"
        ),
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=os.getcwd(),
        help="Directory to save output",
    )
    parser.add_argument(
        "-f",
        "--filename",
        help=(
            "Base filename to use (otherwise derived from title)"
        ),
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save to file; print to stdout",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="HTTP timeout seconds",
    )
    parser.add_argument(
        "--lead-only",
        action="store_true",
        help="Fetch only the lead (intro) section",
    )
    parser.add_argument(
        "--tts-file",
        action="store_true",
        help=(
            "Also produce a TTS-friendly .txt alongside the .md"
        ),
    )
    parser.add_argument(
        "--heading-prefix",
        default=None,
        help=(
            "Prefix for headings in TTS file, e.g. 'Section:'"
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    url = args.url
    if not url.startswith(('http://', 'https://')):
        logger.error('URL must include http:// or https://')
        return

    logger.info('Attempting to extract text from: %s', url)

    result_text, page_title = extract_wikipedia_text(
        url,
        convert_numbers_for_tts=False,
        timeout=args.timeout,
        lead_only=args.lead_only,
    )

    if result_text is None:
        logger.error('Failed to extract text from URL')
        return

    base_name = args.filename or page_title or 'wikipedia_article'
    safe_base = sanitize_filename(base_name)
    md_name = safe_base + '.md'
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
        if args.no_save:
            print(markdown_content)
        else:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            logger.info('Saved markdown to %s', md_path)
            print(f"Output saved to: {md_path}")

            if args.tts_file:
                tts_text = make_tts_friendly(
                    markdown_content, heading_prefix=args.heading_prefix
                )
                tts_path = os.path.splitext(md_path)[0] + '.txt'
                with open(tts_path, 'w', encoding='utf-8') as f:
                    f.write(tts_text)
                logger.info('Saved TTS-friendly text to %s', tts_path)
                print(f"TTS-friendly copy saved to: {tts_path}")

    except IOError as e:
        logger.error('Failed to write output: %s', e)


if __name__ == '__main__':
    main()

