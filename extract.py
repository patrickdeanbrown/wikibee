"""Backward-compatible shim module.

This file keeps the old import path `import extract` working by
re-exporting the public API from the new package module
`wikibee.cli`.
"""

from wikibee import INFLECT_AVAILABLE as INFLECT_AVAILABLE
from wikibee import APIError as APIError
from wikibee import DisambiguationError as DisambiguationError
from wikibee import NetworkError as NetworkError
from wikibee import NotFoundError as NotFoundError
from wikibee import extract_wikipedia_text as extract_wikipedia_text
from wikibee import make_tts_friendly as make_tts_friendly
from wikibee import normalize_for_tts as normalize_for_tts
from wikibee import sanitize_filename as sanitize_filename
from wikibee import write_text_file as write_text_file

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
