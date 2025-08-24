"""Public package API for wikibee.

This module re-exports the public functions and exceptions from
`wikibee.cli` so callers can import directly from
``wikibee`` (and the old top-level `extract` module remains
backwards-compatible).
"""

from . import cli as _cli
from . import formatting as _formatting

# Re-export commonly used names
sanitize_filename = _cli.sanitize_filename
make_tts_friendly = _cli.make_tts_friendly
extract_wikipedia_text = _cli.extract_wikipedia_text
normalize_for_tts = _cli.normalize_for_tts
INFLECT_AVAILABLE = _formatting.INFLECT_AVAILABLE
NetworkError = _cli.NetworkError
APIError = _cli.APIError
NotFoundError = _cli.NotFoundError
DisambiguationError = _cli.DisambiguationError
write_text_file = _formatting.write_text_file

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
