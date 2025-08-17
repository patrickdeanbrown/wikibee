from __future__ import annotations

import argparse
import json
import logging
import os
import re
from typing import Optional, Tuple
from urllib.parse import urlparse, unquote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

try:
    import inflect as _inflect

    _INFLECT_ENGINE = _inflect.engine()
    INFLECT_AVAILABLE = True
except Exception:
    _INFLECT_ENGINE = None
    INFLECT_AVAILABLE = False


# Structured exceptions
class NetworkError(RuntimeError):
    """Network-related errors (requests exceptions)"""


class APIError(RuntimeError):
    """API returned invalid data or JSON decoding failed"""


class NotFoundError(RuntimeError):
    """Page not found or no extract available"""


def _make_session() -> requests.Session:
    """Create a requests Session with retry/backoff and a sensible User-Agent."""
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "POST"}),
    )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({
        "User-Agent": "wiki-extractor/1.0 (https://example.com/)",
    })
    return s


def _parse_title(u: str) -> str:
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


def _fetch_api(
    s: requests.Session, parsed, netloc: str, title: str, lead: bool, to: int
) -> dict:
    api_url = f"{parsed.scheme}://{netloc}/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts|pageprops",
        "format": "json",
        "explaintext": 1,
        "redirects": 1,
        "titles": title,
    }
    if lead:
        params["exintro"] = 1

    resp = s.get(api_url, params=params, timeout=to)
    resp.raise_for_status()
    return resp.json()


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


def sanitize_filename(name: str, max_len: int = 100) -> str:
    """Sanitize a string to be safe as a filename on Windows/Linux/macOS.

    - Removes control characters and problematic punctuation.
    - Replaces whitespace with underscores.
    - Strips leading/trailing dots and spaces.
    - Avoids reserved Windows names.
    - Truncates to max_len.
    """
    if not name:
        return "wikipedia_article"

    # Normalize percent-encoding if present
    try:
        name = unquote(name)
    except Exception:
        pass

    # Remove control characters
    name = re.sub(r'[\x00-\x1f\x7f]', '', name)
    # Remove characters invalid in filenames
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    # Replace whitespace with underscores
    name = re.sub(r'\s+', '_', name)
    # Strip leading/trailing dots and spaces
    name = name.strip(' .')

    if not name:
        name = 'wikipedia_article'

    # Avoid reserved Windows names
    reserved = {
        'CON', 'PRN', 'AUX', 'NUL',
        *(f'COM{i}' for i in range(1, 10)),
        *(f'LPT{i}' for i in range(1, 10)),
    }
    if name.upper() in reserved:
        name = name + '_file'

    # Truncate to max_len while preserving an extension-like suffix
    if len(name) > max_len:
        # Try to preserve a file extension if present (e.g., '.md')
        root, dot, ext = name.rpartition('.')
        if dot and root and len(ext) < 10:
            # allow short extensions
            # keep room for '.' + ext
            keep = max_len - (len(ext) + 1)
            name = root[:keep].rstrip('_') + '.' + ext
        else:
            name = name[:max_len].rstrip('_')

    return name


def normalize_for_tts(text: str, convert_numbers: bool = False) -> str:
    """Apply light normalization to extracted plain text for TTS.

    Performs whitespace collapse and simple cleanup. Number conversion is
    optional and requires an external library (inflect) if requested.
    """
    if not text:
        return ''

    logger.debug('Starting TTS normalization...')

    # Basic whitespace cleanup
    text = text.strip()
    # Collapse multiple blank lines into paragraph breaks
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    # Remove potential leftover list markers
    text = re.sub(r'^\s*[\*#]\s+', '', text, flags=re.MULTILINE)
    # Remove section headers like '== Section ==' left by some exports
    text = re.sub(r'^==+\s*(.*?)\s*==+\s*$', '', text, flags=re.MULTILINE).strip()

    # Optional: convert numbers (requires inflect) - left as placeholder
    if convert_numbers and INFLECT_AVAILABLE:
        try:
            import inflect

            p = inflect.engine()
            # Replace simple integers with words (naive)
            text = re.sub(r'\b(\d+)\b', lambda m: p.number_to_words(m.group(1)), text)
        except Exception:
            logger.debug('Inflect conversion requested but failed')

    logger.debug('Normalization complete.')
    return text.strip()


def make_tts_friendly(markdown: str, heading_prefix: Optional[str] = None) -> str:
    """Convert simple Markdown into a plain text form better suited for TTS.

    - Converts headers like '# Title' to 'Title.' or to
      'Section: Title.' when a `heading_prefix` is provided.
    - Removes Markdown link syntax, emphasis markers and inline code ticks.
    """

    out_lines: list[str] = []
    for line in markdown.splitlines():
        # Headers like '# Title' or '### Subtitle'
        m = re.match(r'^\s*(?P<hashes>#+)\s*(?P<title>.+?)\s*$', line)
        if m:
            title = m.group('title').strip()
            if heading_prefix:
                out_lines.append(f"{heading_prefix} {title}.")
            else:
                out_lines.append(f"{title}.")
            continue

        # Convert Markdown links [text](url) -> text
        line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
        # Remove emphasis markers **bold**, *italic*, __bold__ etc.
        line = re.sub(r'[*_]{1,3}(.+?)[*_]{1,3}', r'\1', line)
        # Inline code `x` -> x
        line = re.sub(r'`(.+?)`', r'\1', line)
        # Remove any remaining leading '#' leftover
        line = re.sub(r'^\s*#+\s*', '', line)
        out_lines.append(line)

    # Collapse multiple blank lines
    text = '\n'.join(out_lines)
    text = re.sub(r'\n\s*\n+', '\n\n', text).strip() + "\n"
    return text


class DisambiguationError(RuntimeError):
    """Raised when the requested title is a disambiguation page.

    This is used when the caller requested an error instead of a
    graceful None return.
    """


def write_text_file(path: str, base_dir: str, content: str) -> None:
    """Safely write a text file ensuring it stays within base_dir.

    Raises ValueError if the resolved path is outside `base_dir` to avoid
    path traversal attacks.
    """
    base_dir = os.path.abspath(base_dir)
    target = os.path.abspath(path)
    if not (target == base_dir or target.startswith(base_dir + os.sep)):
        raise ValueError('Attempt to write outside of output directory')
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, 'w', encoding='utf-8') as f:
        f.write(content)


def extract_wikipedia_text(
    url: str,
    convert_numbers_for_tts: bool = False,
    timeout: int = 15,
    lead_only: bool = False,
    session: Optional[requests.Session] = None,
    raise_on_error: bool = False,
) -> Tuple[Optional[str], Optional[str]]:
    """Fetch and clean text from a Wikipedia article via the MediaWiki API.

    Returns (text, page_title) or (None, page_title) on failure. When
    `raise_on_error` is True this function raises specific exceptions for
    disambiguation, network, or API errors.
    """
    # helper functions are defined at module level
    final_page_title: Optional[str] = None

    # prepare session
    if session is None:
        session = _make_session()

    parsed = urlparse(url)
    title = _parse_title(url)
    netloc = parsed.netloc or "en.wikipedia.org"

    try:
        data = _fetch_api(session, parsed, netloc, title, lead_only, timeout)
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

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        logger.warning("No pages found in API response")
        return None, final_page_title

    page_obj = next(iter(pages.values()))
    return _process_page(page_obj, convert_numbers_for_tts, raise_on_error)


def main():
    """Command-line entry point."""
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
