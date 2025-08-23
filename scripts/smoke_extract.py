r"""Smoke runner: extract a real Wikipedia article and save
`.md` and optional `.txt` TTS-friendly copy.

Usage (PowerShell):
    .\.venv\Scripts\python scripts\smoke_extract.py \
        "https://en.wikipedia.org/wiki/Homer" --tts-file --lead-only -o output
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extract import (
    extract_wikipedia_text,
    make_tts_friendly,
    sanitize_filename,
    write_text_file,
)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Smoke test: extract a real Wikipedia article and " "save outputs"
        ),
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="https://en.wikipedia.org/wiki/Homer",
        help="Article URL",
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
    args = parser.parse_args()

    url = args.url
    out_dir = os.path.abspath(args.output_dir)
    os.makedirs(out_dir, exist_ok=True)

    print(f"Running smoke extract for: {url}")
    text, title = extract_wikipedia_text(
        url, timeout=args.timeout, lead_only=args.lead_only
    )
    if text is None:
        print(f"Extraction failed or returned no text for: {url}")
        return 2

    safe_base = sanitize_filename(title or "wikipedia_article")
    md_path = os.path.join(out_dir, safe_base + ".md")
    tts_path = os.path.join(out_dir, safe_base + ".txt")

    # Write files safely
    try:
        write_text_file(md_path, out_dir, f"# {title}\n\n{text}\n")
        print(f"Wrote markdown to: {md_path}")
        if args.tts_file:
            tts_text = make_tts_friendly(
                f"# {title}\n\n{text}\n", heading_prefix=args.heading_prefix
            )
            write_text_file(tts_path, out_dir, tts_text)
            print(f"Wrote TTS-friendly text to: {tts_path}")
    except Exception as e:
        print(f"Failed to write outputs: {e}")
        return 1

    print("Smoke extraction complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
