r"""Smoke runner that exercises wikibee's extraction pipeline.

By default this script performs two operations:

1. Direct URL extraction for a compact article (Altiplano).
2. Search flow using the query "Antarctic Intermediate Water" and extracting
   the top hit returned by the Wikipedia API.

Markdown (and optional TTS-friendly text) artefacts are written to the chosen
output directory so the results can be inspected manually."""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extract import extract_wikipedia_text, make_tts_friendly, sanitize_filename
from wikibee.client import WikiClient
from wikibee.formatting import write_text_file
from wikibee.tts_openai import TTSClientError, TTSOpenAIClient


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Smoke test: extract a real Wikipedia article and " "save outputs"
        ),
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="https://en.wikipedia.org/wiki/Altiplano",
        help="Article URL to extract (default: Altiplano)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="output",
        help="Directory to save output",
    )
    parser.add_argument(
        "--tts-file",
        action="store_true",
        help="Also save a TTS-friendly .txt",
    )
    parser.add_argument(
        "--heading-prefix",
        default=None,
        help='Prefix for headings in TTS file (e.g. "Section:")',
    )
    parser.add_argument(
        "--lead-only",
        action="store_true",
        help="Fetch only the intro/lead section",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="HTTP timeout",
    )
    parser.add_argument(
        "--search-term",
        default="Antarctic Intermediate Water",
        help="Additional smoke query to verify search-based extraction",
    )
    parser.add_argument(
        "--search-limit",
        type=int,
        default=5,
        help="Maximum results to request when searching",
    )
    parser.add_argument(
        "--skip-search",
        action="store_true",
        help="Skip the search-based extraction step",
    )
    parser.add_argument(
        "--no-tts-audio",
        action="store_true",
        help="Skip synthesizing audio output via the TTS API",
    )
    parser.add_argument(
        "--tts-server",
        default="http://localhost:8880/v1",
        help="Base URL for the TTS server",
    )
    parser.add_argument(
        "--tts-voice",
        default="af_sky+af_bella",
        help="Voice identifier passed to the TTS engine",
    )
    parser.add_argument(
        "--tts-format",
        default="mp3",
        help="Audio format to request from the TTS engine",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Running smoke extract for URL: {args.url}")
    url_status = _extract_and_write(
        source_name="url",
        identifier=args.url,
        url=args.url,
        out_dir=out_dir,
        lead_only=args.lead_only,
        timeout=args.timeout,
        tts_file=args.tts_file,
        heading_prefix=args.heading_prefix,
        tts_audio=not args.no_tts_audio,
        tts_server=args.tts_server,
        tts_voice=args.tts_voice,
        tts_format=args.tts_format,
    )

    search_status = 0
    if not args.skip_search:
        print(f"Running smoke extract for search term: '{args.search_term}'")
        search_status = _search_and_extract(
            term=args.search_term,
            limit=args.search_limit,
            out_dir=out_dir,
            lead_only=args.lead_only,
            timeout=args.timeout,
            tts_file=args.tts_file,
            heading_prefix=args.heading_prefix,
            tts_audio=not args.no_tts_audio,
            tts_server=args.tts_server,
            tts_voice=args.tts_voice,
            tts_format=args.tts_format,
        )

    if url_status or search_status:
        return max(url_status, search_status)

    print("Smoke extraction complete.")
    return 0


def _search_and_extract(
    term: str,
    limit: int,
    out_dir: Path,
    lead_only: bool,
    timeout: int,
    tts_file: bool,
    heading_prefix: Optional[str],
    tts_audio: bool,
    tts_server: str,
    tts_voice: Optional[str],
    tts_format: str,
) -> int:
    client = WikiClient()
    try:
        results = client.search_articles(term, limit=limit, timeout=timeout)
    except Exception as exc:  # pragma: no cover - network smoke
        print(f"Search request failed for '{term}': {exc}")
        return 3

    if not results:
        print(f"No results returned for '{term}'")
        return 3

    top_result = results[0]
    url = top_result["url"]
    identifier = f"search-{sanitize_filename(top_result['title'])}"
    return _extract_and_write(
        source_name="search",
        identifier=identifier,
        url=url,
        out_dir=out_dir,
        lead_only=lead_only,
        timeout=timeout,
        tts_file=tts_file,
        heading_prefix=heading_prefix,
        tts_audio=tts_audio,
        tts_server=tts_server,
        tts_voice=tts_voice,
        tts_format=tts_format,
    )


def _extract_and_write(
    source_name: str,
    identifier: str,
    url: str,
    out_dir: Path,
    lead_only: bool,
    timeout: int,
    tts_file: bool,
    heading_prefix: Optional[str],
    tts_audio: bool,
    tts_server: str,
    tts_voice: Optional[str],
    tts_format: str,
) -> int:
    text, title = extract_wikipedia_text(url, timeout=timeout, lead_only=lead_only)
    if text is None:
        print(f"Extraction failed or returned no text for: {url}")
        return 2

    safe_base = sanitize_filename(title or identifier)
    md_path = out_dir / f"{safe_base}.md"
    tts_path = out_dir / f"{safe_base}.txt"
    audio_path = out_dir / f"{safe_base}.{tts_format}"

    # Write files safely
    try:
        write_text_file(str(md_path), str(out_dir), f"# {title}\n\n{text}\n")
        print(f"[{source_name}] Wrote markdown to: {md_path}")
        if tts_file:
            tts_text = make_tts_friendly(
                f"# {title}\n\n{text}\n", heading_prefix=heading_prefix
            )
            write_text_file(str(tts_path), str(out_dir), tts_text)
            print(f"[{source_name}] Wrote TTS-friendly text to: {tts_path}")
        if tts_audio:
            _write_audio(
                title=title or identifier,
                markdown=f"# {title}\n\n{text}\n",
                audio_path=audio_path,
                out_dir=out_dir,
                tts_server=tts_server,
                tts_voice=tts_voice,
                tts_format=tts_format,
                heading_prefix=heading_prefix,
                tts_file=tts_file,
            )
    except Exception as exc:  # pragma: no cover - smoke diagnostics
        print(f"[{source_name}] Failed to write outputs: {exc}")
        return 1

    return 0


def _write_audio(
    title: str,
    markdown: str,
    audio_path: Path,
    out_dir: Path,
    tts_server: str,
    tts_voice: Optional[str],
    tts_format: str,
    heading_prefix: Optional[str],
    tts_file: bool,
) -> None:
    try:
        tts_client = TTSOpenAIClient(base_url=tts_server)
        tts_ready = make_tts_friendly(
            markdown, heading_prefix=heading_prefix if tts_file else None
        )
        saved = tts_client.synthesize_to_file(
            tts_ready,
            dest_path=str(audio_path.relative_to(out_dir)),
            base_dir=str(out_dir),
            voice=tts_voice,
            file_format=tts_format,
        )
        print(f"[audio] Wrote audio to: {saved}")
    except TTSClientError as exc:
        cause = exc.__cause__ or exc.__context__
        if cause is not None:
            print(f"[audio] TTS synthesis failed: {exc} ({cause})")
        else:
            print(f"[audio] TTS synthesis failed: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
