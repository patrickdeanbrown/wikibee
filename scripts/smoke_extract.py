r"""Smoke runner that exercises wikibee's extraction pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from wikibee.commands import extract as extract_cmd
from wikibee.services import OutputManager, SearchError, SearchService, TTSService
from wikibee.tts_openai import TTSClientError, TTSOpenAIClient


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test: extract real Wikipedia content and save outputs",
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
    output_manager = OutputManager(out_dir, audio_format=args.tts_format)

    print(f"Running smoke extract for URL: {args.url}")
    url_status = _extract_and_write(
        source_name="url",
        identifier=args.url,
        url=args.url,
        output_manager=output_manager,
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
            output_manager=output_manager,
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
    output_manager: OutputManager,
    lead_only: bool,
    timeout: int,
    tts_file: bool,
    heading_prefix: Optional[str],
    tts_audio: bool,
    tts_server: str,
    tts_voice: Optional[str],
    tts_format: str,
) -> int:
    service = SearchService()
    try:
        results = service.search(term, limit=limit, timeout=timeout)
    except SearchError as exc:  # pragma: no cover - network smoke
        print(f"Search request failed for '{term}': {exc}")
        return 3

    if not results:
        print(f"No results returned for '{term}'")
        return 3

    top_result = results[0]
    url = top_result["url"]
    identifier = f"search-{extract_cmd.sanitize_filename(top_result['title'])}"
    return _extract_and_write(
        source_name="search",
        identifier=identifier,
        url=url,
        output_manager=output_manager,
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
    output_manager: OutputManager,
    lead_only: bool,
    timeout: int,
    tts_file: bool,
    heading_prefix: Optional[str],
    tts_audio: bool,
    tts_server: str,
    tts_voice: Optional[str],
    tts_format: str,
) -> int:
    text, title = extract_cmd.extract_wikipedia_text(
        url,
        timeout=timeout,
        lead_only=lead_only,
    )
    if text is None:
        print(f"Extraction failed or returned no text for: {url}")
        return 2

    markdown_content = f"# {title}\n\n{text}\n"
    paths = output_manager.prepare_paths(page_title=title or identifier, filename=None)
    output_manager.write_markdown(paths, markdown_content)
    print(f"[{source_name}] Wrote markdown to: {paths.markdown_path}")

    if tts_file:
        output_manager.write_tts_copy(
            paths,
            markdown_content,
            heading_prefix=heading_prefix,
            normalize=True,
        )
        print(f"[{source_name}] Wrote TTS-friendly text to: {paths.tts_path}")

    if tts_audio:
        service = TTSService(
            client=TTSOpenAIClient(base_url=tts_server),
            output_manager=output_manager,
        )
        try:
            saved = service.synthesize_audio(
                markdown=markdown_content,
                paths=paths,
                heading_prefix=heading_prefix,
                normalize=True,
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
