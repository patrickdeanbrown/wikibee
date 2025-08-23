"""Backward-compatible shim module.

This file keeps the old import path `import extract` working by
re-exporting the public API from the new package module
`wiki_extractor.cli`.
"""

from wiki_extractor import INFLECT_AVAILABLE as INFLECT_AVAILABLE
from wiki_extractor import APIError as APIError
from wiki_extractor import DisambiguationError as DisambiguationError
from wiki_extractor import NetworkError as NetworkError
from wiki_extractor import NotFoundError as NotFoundError
from wiki_extractor import extract_wikipedia_text as extract_wikipedia_text
from wiki_extractor import make_tts_friendly as make_tts_friendly
from wiki_extractor import normalize_for_tts as normalize_for_tts
from wiki_extractor import sanitize_filename as sanitize_filename
from wiki_extractor import write_text_file as write_text_file

__all__ = [
    "sanitize_filename",
    "make_tts_friendly",
    "extract_wikipedia_text",
    "normalize_for_tts",
    "INFLECT_AVAILABLE",
    "NetworkError",
    "APIError",
    "NotFoundError",
    "DisambiguationError",
    "write_text_file",
]
