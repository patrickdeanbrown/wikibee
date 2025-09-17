from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from wikibee import formatting
from wikibee.tts_normalizer import normalize_for_tts as tts_normalize_for_tts

if sys.version_info >= (3, 10):

    @dataclass(slots=True)
    class OutputPaths:
        """Container for output artefact paths."""

        markdown_path: Path
        tts_path: Path
        audio_path: Path

else:

    @dataclass
    class OutputPaths:
        """Container for output artefact paths."""

        markdown_path: Path
        tts_path: Path
        audio_path: Path


class OutputManager:
    """Handle output directory management and derived artefact paths."""

    def __init__(self, base_dir: Path | str, audio_format: str = "mp3") -> None:
        self.base_dir = Path(base_dir).expanduser().resolve()
        self.audio_format = audio_format
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def prepare_paths(self, page_title: str, filename: Optional[str]) -> OutputPaths:
        """Return paths for markdown, TTS text, and audio artefacts."""

        safe_base = formatting.sanitize_filename(filename or page_title)
        markdown_path = self._unique_markdown_path(safe_base)
        tts_path = markdown_path.with_suffix(".txt")
        audio_path = markdown_path.with_suffix(f".{self.audio_format}")
        return OutputPaths(
            markdown_path=markdown_path, tts_path=tts_path, audio_path=audio_path
        )

    def write_markdown(self, paths: OutputPaths, content: str) -> None:
        """Persist markdown content via secure write helper."""

        formatting.write_text_file(
            str(paths.markdown_path), str(self.base_dir), content
        )

    def write_tts_copy(
        self,
        paths: OutputPaths,
        markdown: str,
        *,
        heading_prefix: Optional[str],
        normalize: bool,
    ) -> None:
        """Write a TTS-friendly text file derived from markdown content."""

        source = markdown
        if normalize:
            source = tts_normalize_for_tts(source)
        tts_ready = formatting.make_tts_friendly(source, heading_prefix=heading_prefix)
        formatting.write_text_file(str(paths.tts_path), str(self.base_dir), tts_ready)

    def _unique_markdown_path(self, safe_base: str) -> Path:
        """Return a markdown path, suffixing with _N when collisions occur."""

        candidate = self.base_dir / f"{safe_base}.md"
        if not candidate.exists():
            return candidate

        for index in range(1, 1000):
            alternative = self.base_dir / f"{safe_base}_{index}.md"
            if not alternative.exists():
                return alternative

        raise RuntimeError(f"Unable to allocate unique filename for base '{safe_base}'")
